import json

from dobiss_entity_helper import get_entities
from mqtt.mqtt_helper import get_mqtt_client
from objects.dobiss_dimmer import DobissDimmer
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relay import DobissRelay


def publish_discovery_topics_for_entities(client, entities):
    for entity_name in entities:
        entity = entities[entity_name]
        mqtt_name = entity.get_mqtt_name()
        if type(entity) is DobissRelay or type(entity) is DobissDimmer:
            if type(entity) is DobissRelay:
                discover_payload = {
                    "name": mqtt_name,
                    "command_topic": f"homeassistant/light/{mqtt_name}/set",
                    "state_topic": f"homeassistant/light/{mqtt_name}/state",
                    "payload_on": "1",
                    "payload_off": "0",
                    "unique_id": mqtt_name
                }
            elif type(entity) is DobissDimmer:
                discover_payload = {
                    "name": mqtt_name,
                    "command_topic": f"homeassistant/light/{mqtt_name}/set",
                    "state_topic": entity.get_mqtt_state_topic(),
                    "payload_on": "1",
                    "payload_off": "0",
                    "unique_id": mqtt_name,
                    "brightness_command_topic": f"home/light/{mqtt_name}/brightness/set",
                    "brightness_state_topic": f"home/light/{mqtt_name}/brightness/state",
                    "on_command_type": "brightness",
                    "brightness_scale": entity.max_brightness
                }
            else:
                raise Exception(f"Unknown entity type: {type(entity)}")
            discover_topic = f"homeassistant/light/{mqtt_name}/config"
            client.publish(discover_topic, json.dumps(discover_payload), retain=True)
            topic = entity.get_mqtt_state_topic()
            payload = entity.current_status
            client.publish(topic, payload, retain=True)


if __name__ == '__main__':
    publish_discovery_topics_for_entities(get_mqtt_client(), get_entities())
