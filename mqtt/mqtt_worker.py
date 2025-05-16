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
        self.client = self.initialize_mqtt_client(MqttWorker.process_received_message)
        self.receive_thread = Thread(target=MqttWorker.receive, args=(self,))
        self.receive_thread.start()
        self.worker_thread = Thread(target=MqttWorker.work, args=(self,))
        self.worker_thread.start()

    @staticmethod
    def initialize_mqtt_client(on_message_callback):
        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.on_message = on_message_callback
        client.tls_set()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe("homeassistant/light/+/set")  # Subscribe to commands to set the light status.
        logger.debug("Initialed MQTT client")
        return client

    @staticmethod
    def get_mqtt_worker():
        global _mqtt_worker
        if _mqtt_worker is None:
            _mqtt_worker = MqttWorker()
        return _mqtt_worker

    def publish_discovery_topics(self, entities):
        publish_discovery_topics_for_entities(self.client, entities)
        self.client.subscribe("homeassistant/light/+/set")  # Subscribe to commands to set the light status.

    def work(self):
        while True:
            (topic, message) = self.publish_queue.get()
            logger.debug(f"Publish state change to MQTT ({topic}, {message}).")
            self.client.publish(topic, message)

    def receive(self):
        logger.debug("MQTT receive thread started")
        self.client.loop_forever()

    @staticmethod
    def process_received_message(client, userdata, msg):
        from dobiss_entity_helper import get_entities
        entities = get_entities()
        topic = msg.topic
        status = msg.payload.decode()
        entity_name = topic.replace('homeassistant/light/', '').replace('/set', '')
        logger.debug(f"Received topic {topic}, payload: {status}, entity_name: {entity_name}")
        print(entities.keys())
        if entity_name in entities.keys():
            entities[entity_name].set_status(int(status))
        else:
            logger.error(f"Failed to process mqtt topic: {topic}")
