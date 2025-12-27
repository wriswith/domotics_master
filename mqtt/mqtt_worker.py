import json
import time
import traceback
from queue import Queue
from threading import Thread
from typing import cast

import paho.mqtt.client as mqtt

from config.config import MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT
from logger import logger
from mqtt.publish_discovery_topics import publish_discovery_topics_for_entities
from objects.dobiss_fan import DobissFan

_mqtt_worker = None


class MqttWorker:
    def __init__(self):
        logger.debug("Creating MqttWorker")
        self.publish_queue = Queue()
        self.receive_thread = Thread(target=MqttWorker.receive, args=(self,))
        self.receive_thread.start()
        self.publish_thread = Thread(target=MqttWorker.publish, args=(self,))
        self.publish_thread.start()

    @staticmethod
    def initialize_mqtt_client(on_message_callback, subscribe_topics=()):
        try:
            client = mqtt.Client()
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
            client.on_message = on_message_callback
            client.tls_set()
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            logger.debug("Initialed MQTT client")
            for topic in subscribe_topics:
                client.subscribe(topic)
            return client
        except Exception as e:
            logger.error(f"MQTT client failed to initialize with error: {e}")
            # Upon exception create a new connection.
            traceback.print_exc()
            time.sleep(120)
            return MqttWorker.initialize_mqtt_client(on_message_callback, subscribe_topics)

    @staticmethod
    def get_mqtt_worker():
        global _mqtt_worker
        if _mqtt_worker is None:
            _mqtt_worker = MqttWorker()
        return _mqtt_worker

    def publish_discovery_topics(self, entities):
        publish_discovery_topics_for_entities(self.publish_queue, entities)
        time.sleep(0.5)

    def publish(self):
        """
        Thread that maintains an MQTT client to publish the MQTT messages that are put into the self.publish_queue to
        the MQTT broker.
        :return:
        """
        client = self.initialize_mqtt_client(MqttWorker.process_received_message)
        client.loop_start()
        while True:
            message = ''
            topic = ''
            try:
                (topic, message, retain) = self.publish_queue.get()
                logger.debug(f"Publish state change to MQTT ({topic}, {message}).")
                client.publish(topic, message, retain=retain)
            except Exception as e:
                logger.error(f"Failed to publish {message} to {topic}. ({e})")
                # Upon exception create a new connection.
                traceback.print_exc()
                client.loop_stop()
                client.disconnect()
                client = self.initialize_mqtt_client(MqttWorker.process_received_message)
                client.loop_start()

    def receive(self):
        """
        Thread that maintains the MQTT client to receive messages from the MQTT broker by subscribing to the relevant
        MQTT topics. When a message is received, the function process_received_message is called by the client.
        :return:
        """
        # Use separate client as the MQTT client is not thread safe.
        client = self.initialize_mqtt_client(MqttWorker.process_received_message,
                                             ["homeassistant/light/+/set", "homeassistant/cover/+/set"])
        logger.debug("MQTT receive thread started")
        while True:
            try:
                client.loop_forever()
            except Exception as e:
                logger.error(f"MQTT receive client failed with error: {e}")
                # Upon exception create a new connection.
                traceback.print_exc()
                client.disconnect()
                time.sleep(3)
                client = self.initialize_mqtt_client(MqttWorker.process_received_message,
                                                     ["homeassistant/light/+/set",
                                                      "homeassistant/cover/+/set"])  # Subscribe to commands to set the light status.

    @staticmethod
    def process_received_message(client, userdata, msg):
        """
        Function to process MQTT set messages from Home Assistant. The entity name is stripped from the topic.
        :param client:
        :param userdata:
        :param msg:
        :return:
        """
        from dobiss_entity_helper import get_entities
        from objects.dobiss_entity import DobissEntity
        logger.debug(f"Received topic {msg.topic}, payload: {msg.payload.decode()}")

        entities = get_entities()

        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        fan_prefix = 'homeassistant/fan/'
        if topic.startswith(fan_prefix):
            topic_parts = topic[len(fan_prefix):].split('/')
            entity_name = topic_parts[0]
            fan = cast(DobissFan, entities[entity_name])
            if topic_parts[1] == 'preset':
                fan.set_preset(payload.get("preset"))
            elif topic_parts[1] == 'set':
                fan.set_status(DobissEntity.convert_status_from_mqtt(payload.get("state")))
            else:
                raise NotImplementedError(f"Unable to handle topic: {topic}")
        else:
            entity_name = topic[20:-4]

            if entity_name not in entities.keys():
                logger.error(f"Failed to process mqtt topic due to unknown entity name {entity_name}: {topic}")
                return

            raw_payload = msg.payload.decode()
            if raw_payload[:1] == "{":
                try:
                    payload = json.loads(msg.payload.decode())
                except Exception as e:
                    logger.error(f"Failed to parse payload of topic {topic} as JSON ({msg.payload.decode()})")
                    raise e
                status = DobissEntity.convert_status_from_mqtt(payload.get("state"))
                brightness = payload.get("brightness")
            else:
                status = raw_payload
                brightness = None

            # Handle binary on of switch
            if brightness is None:
                logger.debug(f"Setting {entity_name} to {status}")
                entities[entity_name].set_status(status)

            # Handle JSON response
            else:
                logger.debug(f"Setting {entity_name} to {status} and {brightness}.")
                entities[entity_name].set_status(status, brightness)
