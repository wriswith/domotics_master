import paho.mqtt.client as mqtt

from config.config import MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT

_client = None


def get_mqtt_client():
    global _client
    if _client is None:
        _client = mqtt.Client()
        _client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        # _client.on_message = on_message  # Function that handles msgs from subscribed MQTT topics
        _client.tls_set()
        _client.connect(MQTT_BROKER, MQTT_PORT, 60)
        # _client.subscribe(TOPIC_SUB)
    return _client
