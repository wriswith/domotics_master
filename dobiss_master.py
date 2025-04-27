from queue import Queue

from can_bus_control import update_status_of_entities
from config.config import ACTIVE_PICO_PINS
from objects.dobiss_entity import DobissEntity
from config.dobiss_entity_config import DOBISS_LIGHTS_CONFIG
from one_wire_reader import one_wire_reader


def dobiss_master():
    dobiss_entities = generate_dobiss_entities()
    update_status_of_entities(dobiss_entities)
    switch_event_queue = Queue()
    one_wire_reader(ACTIVE_PICO_PINS, switch_event_queue)

    # load config to translate light switches to lights
    # Start listening for light switches
    # respond to light switch events



def generate_dobiss_entities():
    dobiss_entities = {}
    for name in DOBISS_LIGHTS_CONFIG:
        dobiss_entities[name] = DobissEntity.config_to_dobiss_entity(DOBISS_LIGHTS_CONFIG[name], name)
    return dobiss_entities


if __name__ == '__main__':
    dobiss_master()
