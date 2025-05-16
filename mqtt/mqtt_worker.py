from queue import Queue
from threading import Thread

import paho.mqtt.client as mqtt

from config.config import MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT
from mqtt.publish_discovery_topics import publish_discovery_topics_for_entities


_mqtt_worker = None


class MqttWorker:
    def __init__(self):
        self.publish_queue = Queue()
        self.client = self.initialize_mqtt_client()
        self.worker_thread = Thread(target=MqttWorker.work, args=(self,))
        self.worker_thread.start()

    @staticmethod
    def initialize_mqtt_client():
        client = mqtt.Client()
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        # self.client.on_message = on_message  # Function that handles msgs from subscribed MQTT topics
        client.tls_set()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        # self.client.subscribe(TOPIC_SUB)
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
