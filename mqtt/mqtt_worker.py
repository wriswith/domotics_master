import json
import time
import traceback
from queue import Queue
from threading import Thread

import paho.mqtt.client as mqtt

from config.config import MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT
from logger import logger
from mqtt.publish_discovery_topics import publish_discovery_topics_for_entities


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
    def initialize_mqtt_client(on_message_callback):
        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.on_message = on_message_callback
        client.tls_set()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        logger.debug("Initialed MQTT client")
        return client

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
        # Use separate client as the MQTT client is not thread safe.
        client = self.initialize_mqtt_client(MqttWorker.process_received_message)
        client.subscribe("homeassistant/light/+/set")  # Subscribe to commands to set the light status.
        logger.debug("MQTT receive thread started")
        while True:
            try:
                client.loop_forever()
            except Exception as e:
                logger.error(f"MQTT receive client failed with error: {e}")
                # Upon exception create a new connection.
                traceback.print_exc()
                client.disconnect()
                client = self.initialize_mqtt_client(MqttWorker.process_received_message)
                client.subscribe("homeassistant/light/+/set")  # Subscribe to commands to set the light status.

    @staticmethod
    def process_received_message(client, userdata, msg):
        from dobiss_entity_helper import get_entities
        from objects.dobiss_entity import DobissEntity
        logger.debug(f"Received topic {msg.topic}, payload: {msg.payload.decode()}")

        entities = get_entities()

        topic = msg.topic
        entity_name = topic[20:-4]

        payload = json.loads(msg.payload.decode())
        status = DobissEntity.convert_status_from_mqtt(payload.get("state"))
        brightness = payload.get("brightness")

        if entity_name not in entities.keys():
            logger.error(f"Failed to process mqtt topic: {topic}")

        # Handle binary on of switch
        elif brightness is None:
            logger.debug(f"Setting {entity_name} to {status}")
            entities[entity_name].set_status(status)

        # Handle JSON response
        else:
            logger.debug(f"Setting {entity_name} to {status} and {brightness}.")
            entities[entity_name].set_status(status, brightness)
