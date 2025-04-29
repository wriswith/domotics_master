
DOBISS_RELAY = 'relay'
DOBISS_DIMMER = 'dimmer'
DOBISS_SCENE = 'scene'
DOBISS_SHADE = 'shade'
LIGHT = 'light'
VENTILATION = 'fan'
SHADE = 'cover'


DOBISS_LIGHTS_CONFIG = {
    "TV Wand": {"module": 1, "output": 1, "dobiss_type": DOBISS_DIMMER, "ha_type": LIGHT},
    "Bureau Beestje": {"module": 1, "output": 2, "dobiss_type": DOBISS_DIMMER, "ha_type": LIGHT},
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
    "Ventilatie": {"module": 4, "output": 3, "dobiss_type": DOBISS_RELAY, "ha_type": VENTILATION},
    "Boost": {"module": 4, "output": 4, "dobiss_type": DOBISS_RELAY, "ha_type": VENTILATION},
}

DOBISS_SHADES_CONFIG = {
  "Shade_Salon": {"output_up": {"module": 2, "output": 6}, "output_down": {"module": 2, "output": 7}, "dobiss_type": DOBISS_SHADE, "ha_type": SHADE},
  "Shade_Speelkamer": {"output_up": {"module": 2, "output": 10}, "output_down": {"module": 2, "output": 11}, "dobiss_type": DOBISS_SHADE, "ha_type": SHADE},
  "Shade_Slaapkamer Ouders": {"output_up": {"module": 4, "output": 7}, "output_down": {"module": 4, "output": 6}, "dobiss_type": DOBISS_SHADE, "ha_type": SHADE},
}

DOBISS_SCENES_CONFIG = {
    "Alles uit": [],
    "Boven uit": [
                    ("Bureau Beestje", (0, )),
                    ("Slaapkamer Daniel", (0, )),
                    ("Slaapkamer Ouders", (0, )),
                    ("Trap", (0, )),
                    ("Dressing", (0, )),
                    ("Spiegel", (0, )),
                    ("Badkamer", (0, )),
                    ("Douche", (0, )),
                    ("Wasplaats", (0, )),
                    ("Technische Ruimte", (0, )),
                    ("Zolder", (0, )),
                  ],
}


def generate_alles_uit_scene():
    for light_name in DOBISS_LIGHTS_CONFIG.keys():
        DOBISS_SCENES_CONFIG["Alles uit"].append((light_name, (0, )))


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


DOBISS_MODULE_OVERVIEW = pivot_config(DOBISS_LIGHTS_CONFIG)
