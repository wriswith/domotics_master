import json
from queue import Queue

from mqtt.mqtt_helper import get_mqtt_client


def publish_discovery_topics_for_entities(publish_queue: Queue, entities):
    from objects.dobiss_dimmer import DobissDimmer
    from objects.dobiss_relay import DobissRelay
    from objects.dobiss_output import DobissOutput
    for entity_name in entities:
        entity = entities[entity_name]
        if isinstance(entity, DobissOutput):
            if type(entity) is DobissRelay:
                discover_payload = {
                    "name": entity_name,
                    "command_topic": entity.get_mqtt_command_topic(),
                    "state_topic": entity.get_mqtt_state_topic(),
                    "payload_on": 1,
                    "payload_off": 0,
                    "unique_id": entity_name,
                    "schema": "json",
                }
            elif type(entity) is DobissDimmer:
                discover_payload = {
                    "name": entity_name,
                    "unique_id": entity_name,
                    "command_topic": entity.get_mqtt_command_topic(),
                    "state_topic": entity.get_mqtt_state_topic(),
                    "schema": "json",
                    "on_command_type": "brightness",
                    "brightness": True,
                    "brightness_scale": entity.max_brightness,
                    "payload_on": 1,
                    "payload_off": 0
                }
            else:
                raise Exception(f"Unknown entity type: {type(entity)}")
            discover_topic = f"homeassistant/light/{entity_name}/config"
            publish_queue.put((discover_topic, json.dumps(discover_payload), True))
            entity.report_state_to_mqtt()


if __name__ == '__main__':
    from dobiss_entity_helper import get_entities
    publish_discovery_topics_for_entities(get_mqtt_client(), get_entities())
