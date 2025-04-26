
DOBISS_RELAY = 'relay'
DOBISS_DIMMER = 'dimmer'
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
  # "Boost": {"module": 4, "output": 4, "dobiss_type": DOBISS_RELAY, "ha_type": VENTILATION},
}

DOBISS_SHADES_CONFIG = {
  "Salon": {"output_up": {"module": 2, "output": 6}, "output_down": {"module": 2, "output": 7}, "dobiss_type": DOBISS_RELAY, "ha_type": SHADE},
  "Speelkamer": {"output_up": {"module": 2, "output": 10}, "output_down": {"module": 2, "output": 11}, "dobiss_type": DOBISS_RELAY, "ha_type": SHADE},
  "Slaapkamer Ouders": {"output_up": {"module": 4, "output": 7}, "output_down": {"module": 4, "output": 6}, "dobiss_type": DOBISS_RELAY, "ha_type": SHADE},
}

DOBISS_MODULES = {
  1: {'type': DOBISS_DIMMER, 'id': 0x00400102},
  2: {'type': DOBISS_RELAY, 'id': 0x00200202},
  3: {'type': DOBISS_RELAY, 'id': 0x00200302},
  4: {'type': DOBISS_RELAY, 'id': 0x00200402},
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
