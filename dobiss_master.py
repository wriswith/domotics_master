import time
from queue import Queue

from can_bus_control import update_status_of_entities, switch_dobiss_entity
from config.button_entity_mapping import BUTTON_ENTITY_MAP
from config.config import ACTIVE_PICO_PINS, SHORT_PRESS_CUTOFF, BUTTON_LOCKOUT_PERIOD
from logger import logger
from objects.dobiss_entity import DobissEntity
from config.dobiss_entity_config import DOBISS_LIGHTS_CONFIG
from objects.switch_event import SWITCH_ACTION_RELEASE
from one_wire_reader import one_wire_reader


def dobiss_master():
    dobiss_entities = generate_dobiss_entities()
    button_entity_map = create_button_entity_map(dobiss_entities)
    update_status_of_entities(dobiss_entities)
    switch_event_queue = Queue()
    one_wire_reader(ACTIVE_PICO_PINS, switch_event_queue)
    handle_button_events(switch_event_queue, button_entity_map)


def handle_button_events(switch_event_queue, button_entity_map):
    lockout_timestamp = None  # Variable to set an epoch before which all buttons should be ignored (to avoid double clicks)
    while True:
        switch_event = switch_event_queue.get()
        if lockout_timestamp is not None:
            if time.time() < lockout_timestamp:
                logger.debug(f"Dropping a button in the lockout period.")
                continue
            else:
                lockout_timestamp = None

        if switch_event.action == SWITCH_ACTION_RELEASE:
            click_mode = 'short'
            if switch_event.duration > SHORT_PRESS_CUTOFF:
                click_mode = 'long'
            entity = button_entity_map[switch_event.button_name][click_mode]
            logger.info(f"Switching {entity.name} after {click_mode} click on {switch_event.button_name}")
            switch_dobiss_entity(button_entity_map[switch_event.button_name][click_mode])
            lockout_timestamp = time.time() + BUTTON_LOCKOUT_PERIOD  # ignore button presses for the next 0.2 seconds to avoid double releases


def create_button_entity_map(dobiss_entities: dict):
    """
    Create a dict with a key for every button name and as element the proper entity object to trigger upon short or long press.
    :param dobiss_entities:
    :return:
    """
    button_entity_map = {}
    for button_name in BUTTON_ENTITY_MAP:
        button_entity_map[button_name] = {}
        if BUTTON_ENTITY_MAP[button_name]['short'] is None:
            button_entity_map[button_name]['short'] = None
        else:
            button_entity_map[button_name]['short'] = dobiss_entities[BUTTON_ENTITY_MAP[button_name]['short']]

        if BUTTON_ENTITY_MAP[button_name]['long'] is None:
            button_entity_map[button_name]['long'] = None
        else:
            button_entity_map[button_name]['long'] = dobiss_entities[BUTTON_ENTITY_MAP[button_name]['long']]
    return button_entity_map


def generate_dobiss_entities():
    """
    Create a dict of entity objects based on the dict DOBISS_LIGHTS_CONFIG in the config file.
    :return:
    """
    dobiss_entities = {}
    for name in DOBISS_LIGHTS_CONFIG:
        dobiss_entities[name] = DobissEntity.config_to_dobiss_entity(DOBISS_LIGHTS_CONFIG[name], name)
    return dobiss_entities


if __name__ == '__main__':
    dobiss_master()
