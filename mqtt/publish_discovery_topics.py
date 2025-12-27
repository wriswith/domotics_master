import json
from queue import Queue
from typing import cast

from config.constants import SHADE_COMMAND_UP, SHADE_COMMAND_STOP, SHADE_COMMAND_DOWN, SHADE_STATE_UP, \
    SHADE_STATE_DOWN, SHADE_STATE_GOING_DOWN, SHADE_STATE_GOING_UP, SHADE_STATE_STOPPED, LIGHT
from mqtt.mqtt_helper import get_mqtt_client
from objects.dobiss_scene import DobissScene


def publish_discovery_topics_for_entities(publish_queue: Queue, entities):
    from objects.dobiss_dimmer import DobissDimmer
    from objects.dobiss_relay import DobissRelay
    from objects.dobiss_shade import DobissShade
    from objects.dobiss_fan import DobissFan
    for entity_name in entities:
        entity = entities[entity_name]
        if type(entity) is DobissRelay:
            domain = "light"
            discover_payload = {
                "name": entity_name,
                "command_topic": entity.get_mqtt_command_topic(),
                "state_topic": entity.get_mqtt_state_topic(),
                "payload_on": 1,
                "payload_off": 0,
                "unique_id": entity_name,
                "schema": "json",
                "retain": False,
            }
        elif type(entity) is DobissDimmer:
            domain = "light"
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
                "payload_off": 0,
                "retain": False,
            }
        elif type(entity) is DobissShade:
            domain = "cover"
            discover_payload = {
              "name": entity_name,
              "unique_id": entity_name,
              "command_topic": entity.get_mqtt_command_topic(),
              "state_topic": entity.get_mqtt_state_topic(),
              # "position_topic": entity.get_mqtt_position_topic(),
              # "set_position_topic": entity.get_mqtt_set_position_topic(),
              "payload_open": SHADE_COMMAND_UP,
              "payload_close": SHADE_COMMAND_DOWN,
              "payload_stop": SHADE_COMMAND_STOP,
              "state_open": SHADE_STATE_UP,
              # "position_open": 0,
              "state_closed": SHADE_STATE_DOWN,
              # "position_closed": 100,
              "state_closing": SHADE_STATE_GOING_DOWN,
              "state_opening": SHADE_STATE_GOING_UP,
              "state_stopped": SHADE_STATE_STOPPED,
              "device_class": "shade",
              "retain": False,
            }
        elif type(entity) is DobissFan:
            entity = cast(DobissFan, entity)
            domain = "fan"
            discover_payload = {
                "name": entity_name,
                "unique_id": entity_name,
                "command_topic": entity.get_mqtt_command_topic(),
                "state_topic": entity.get_mqtt_state_topic(),
                "preset_modes": entity.get_preset_modes(),
                "preset_mode_command_topic": entity.get_mqtt_preset_command_topic(),
                "preset_mode_state_topic": entity.get_mqtt_preset_state_topic(),
                "device_class": "fan",
                "payload_on": 1,
                "payload_off": 0,
                "schema": "json",
                "retain": False,
            }
        elif type(entity) is DobissScene:
            continue  # ignore DobissScene
        else:
            raise Exception(f"Unknown entity type: {type(entity)}")
        discover_topic = f"homeassistant/{domain}/{entity_name}/config"
        publish_queue.put((discover_topic, json.dumps(discover_payload), True))
        entity.report_state_to_mqtt()
