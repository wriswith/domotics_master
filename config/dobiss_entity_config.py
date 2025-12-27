from config.constants import DOBISS_RELAY, DOBISS_DIMMER, DOBISS_SHADE, LIGHT, VENTILATION, SHADE, ACTION_SWITCH, \
    ACTION_TURN_ON, ACTION_TURN_OFF, ACTION_SCHEDULE

DOBISS_LIGHTS_CONFIG = {
    "TV Wand": {"module": 1, "output": 1, "dobiss_type": DOBISS_DIMMER, "ha_type": LIGHT},
    "Bureau Beestje": {"module": 1, "output": 2, "dobiss_type": DOBISS_DIMMER, "ha_type": LIGHT, "max_brightness": 85, "min_brightness": 1},
    "Slaapkamer Daniel": {"module": 1, "output": 3, "dobiss_type": DOBISS_DIMMER, "ha_type": LIGHT},
    "Slaapkamer Ouders": {"module": 1, "output": 4, "dobiss_type": DOBISS_DIMMER, "ha_type": LIGHT},
    "Hal": {"module": 2, "output": 2, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Toilet": {"module": 2, "output": 3, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "TV spots": {"module": 2, "output": 4, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Eetkamer": {"module": 2, "output": 5, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Speelkamer": {"module": 2, "output": 8, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Voordeur": {"module": 2, "output": 9, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Berging": {"module": 2, "output": 12, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Keuken": {"module": 3, "output": 1, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Ledstrip": {"module": 3, "output": 2, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Keuken Spots": {"module": 3, "output": 3, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Garage": {"module": 3, "output": 4, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Bureau Pruts": {"module": 3, "output": 5, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Trap": {"module": 3, "output": 7, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Dressing": {"module": 3, "output": 8, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Spiegel": {"module": 3, "output": 9, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Badkamer": {"module": 3, "output": 10, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Douche": {"module": 3, "output": 11, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Wasplaats": {"module": 3, "output": 12, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Technische Ruimte": {"module": 4, "output": 1, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
    "Zolder": {"module": 4, "output": 2, "dobiss_type": DOBISS_RELAY, "ha_type": LIGHT},
}

DOBISS_SHADES_CONFIG = {
  "Shade_Salon": {"output_up": {"module": 2, "output": 6}, "output_down": {"module": 2, "output": 7}, "speed_up": 13, "speed_down": 14, "dobiss_type": DOBISS_SHADE, "ha_type": SHADE},
  "Shade_Speelkamer": {"output_up": {"module": 2, "output": 10}, "output_down": {"module": 2, "output": 11}, "speed_up": 9, "speed_down": 11, "dobiss_type": DOBISS_SHADE, "ha_type": SHADE},
  "Shade_Slaapkamer Ouders": {"output_up": {"module": 4, "output": 7}, "output_down": {"module": 4, "output": 6}, "speed_up": 9, "speed_down": 10.5, "dobiss_type": DOBISS_SHADE, "ha_type": SHADE},
}

DOBISS_FAN_CONFIG = {
    "Ventilatie": {"module": 4, "output": 3, "presets": {"boost": {"module": 4, "output": 4}}, "ha_type": VENTILATION},
}

DOBISS_SCENES_CONFIG = {
    "SCENE Alles uit": [],
    "SCENE Boven uit": [
                    ("Bureau Beestje", ACTION_TURN_OFF),
                    ("Slaapkamer Daniel", ACTION_TURN_OFF),
                    ("Slaapkamer Ouders", ACTION_TURN_OFF),
                    ("Trap", ACTION_TURN_OFF),
                    ("Dressing", ACTION_TURN_OFF),
                    ("Spiegel", ACTION_TURN_OFF),
                    ("Badkamer", ACTION_TURN_OFF),
                    ("Douche", ACTION_TURN_OFF),
                    ("Wasplaats", ACTION_TURN_OFF),
                    ("Technische Ruimte", ACTION_TURN_OFF),
                    ("Zolder", ACTION_TURN_OFF),
                  ],
    "SCENE Beneden uit": [
                    ("TV Wand", ACTION_TURN_OFF),
                    ("Hal", ACTION_TURN_OFF),
                    ("Toilet", ACTION_TURN_OFF),
                    ("TV spots", ACTION_TURN_OFF),
                    ("Eetkamer", ACTION_TURN_OFF),
                    ("Speelkamer", ACTION_TURN_OFF),
                    ("Voordeur", ACTION_TURN_OFF),
                    ("Berging", ACTION_TURN_OFF),
                    ("Keuken", ACTION_TURN_OFF),
                    ("Ledstrip", ACTION_TURN_OFF),
                    ("Keuken Spots", ACTION_TURN_OFF),
                    ("Garage", ACTION_TURN_OFF),
                    ("Bureau Pruts", ACTION_TURN_OFF),
                  ],
    "SCENE douche": [
                    ("Douche", ACTION_SWITCH),
                    ("Boost", ACTION_TURN_ON),
                    ("Boost", ACTION_SCHEDULE, {"delay": 1800, "real_action": ACTION_TURN_OFF, "named_arguments": {}}),
                  ],
}


def generate_alles_uit_scene():
    """
    Add a turn-off action for all non ventilation outputs to the "Alles uit" scene. Add pulsing garage light to signal
    to the user that the scene was triggered.
    """
    DOBISS_SCENES_CONFIG["SCENE Alles uit"].extend([
        ("Garage", ACTION_TURN_OFF),
        ("Garage", ACTION_SCHEDULE, {"delay": 1, "real_action": ACTION_SWITCH, "named_arguments": {}}),
        ("Garage", ACTION_SCHEDULE, {"delay": 2, "real_action": ACTION_SWITCH, "named_arguments": {}}),
        ("Garage", ACTION_SCHEDULE, {"delay": 3, "real_action": ACTION_SWITCH, "named_arguments": {}}),
        ("Garage", ACTION_SCHEDULE, {"delay": 5, "real_action": ACTION_TURN_OFF, "named_arguments": {}}),
    ])
    for light_name in DOBISS_LIGHTS_CONFIG.keys():
        if DOBISS_LIGHTS_CONFIG[light_name]["ha_type"] != VENTILATION and light_name != "Garage":
            DOBISS_SCENES_CONFIG["SCENE Alles uit"].append((light_name, ACTION_TURN_OFF))


generate_alles_uit_scene()

# List of all the modules in the system. Every module has the following attributes
# module_number: The module number as used in the dobiss configuration software
# type Not currently used
# id: The id of the module as used in the CAN-bus protocol. Can be detected by listening to the bus and using the app to switch relays.
# nr_response_messages: The number of CAN-bus messages needed to report the status of all the relays on the module.

DOBISS_MODULES = {
  1: {'module_number': 1, 'type': DOBISS_DIMMER, 'id': 0x00400102, 'nr_response_messages': 1},
  2: {'module_number': 2, 'type': DOBISS_RELAY, 'id': 0x00200202, 'nr_response_messages': 2},
  3: {'module_number': 3, 'type': DOBISS_RELAY, 'id': 0x00200302, 'nr_response_messages': 2},
  4: {'module_number': 4, 'type': DOBISS_RELAY, 'id': 0x00200402, 'nr_response_messages': 2},
}


def pivot_config(config):
    result = {}
    for entity_name in config:
        module = config[entity_name]["module"]
        output = config[entity_name]["output"]
        if module not in result:
            result[module] = {output: entity_name}
        else:
            result[module][output] = entity_name
    return result
