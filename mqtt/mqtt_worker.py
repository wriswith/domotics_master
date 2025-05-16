from queue import Queue
from threading import Thread

import paho.mqtt.client as mqtt

from config.config import MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT
from logger import logger
from mqtt.publish_discovery_topics import publish_discovery_topics_for_entities


_mqtt_worker = None


class MqttWorker:
    def __init__(self):
        self.publish_queue = Queue()
        self.client = self.initialize_mqtt_client(MqttWorker.process_received_message)
        self.receive_thread = Thread(target=MqttWorker.receive, args=(self,))
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
        return client

    @staticmethod
    def get_mqtt_worker():
        global _mqtt_worker
        if _mqtt_worker is None:
            _mqtt_worker = MqttWorker()
        return _mqtt_worker

    def publish_discovery_topics(self, entities):
        publish_discovery_topics_for_entities(self.client, entities)

    def work(self):
        while True:
            (topic, message) = self.publish_queue.get()
            self.client.publish(topic, message)

    def receive(self):
        self.client.loop_forever()

    @staticmethod
    def process_received_message(client, userdata, msg):
        from dobiss_entity_helper import get_entities
        entities = get_entities()
        topic = msg.topic
        status = msg.payload.decode()
        logger.debug(f"Received topic {topic}, payload: {status}")
        entity_name = topic.replace('homeassistant/light/_mqtt_', '').replace('/set', '')
        if entity_name in entities:
            entities[entity_name].set_status(status)
        else:
            logger.error(f"Failed to process mqtt topic: {topic}")
