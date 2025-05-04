import time
from queue import Queue

from can_bus_control import get_modules_statuses
from config.button_entity_mapping import BUTTON_ENTITY_MAP
from config.config import ACTIVE_PICO_PINS, SHORT_PRESS_CUTOFF, BUTTON_LOCKOUT_PERIOD
from config.constants import ACTION_SWITCH
from dobiss_entity_helper import get_entities, parse_module_status_response
from logger import logger
from objects.entity_action import EntityAction
from objects.switch_event import SWITCH_ACTION_RELEASE
from one_wire_reader import one_wire_reader


def dobiss_master():
    # Create the mapping between the buttons and the possible actions
    button_entity_map = create_button_entity_map()

    # Read the current status of the entities from the modules using CAN bus
    modules_statuses = get_modules_statuses()
    for module_number in modules_statuses:
        parse_module_status_response(modules_statuses[module_number], module_number)

    # Start reading button events from the pico pi
    switch_event_queue = Queue()
    one_wire_reader(ACTIVE_PICO_PINS, switch_event_queue)

    # Execute the actions related to the button events
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
            try:
                logger.info(f"Switching {entity.name} after {click_mode} click on {switch_event.button_name}")
                entity.switch_status()
            except Exception as e:
                logger.error(f"Failed to switch {entity}: {e}")
            lockout_timestamp = time.time() + BUTTON_LOCKOUT_PERIOD  # ignore button presses for the next 0.2 seconds to avoid double releases


def create_button_entity_map():
    """
    Create a dict with a key for every button name and as element the proper entity object to trigger upon short or long press.
    :return:
    """
    logger.debug(f"Creating button entity map")
    button_entity_map = {}
    for button_name in BUTTON_ENTITY_MAP:
        button_entity_map[button_name] = {}
        button_entity_map[button_name]['short'] = convert_tuple_to_action_object(BUTTON_ENTITY_MAP[button_name]['short'])
        button_entity_map[button_name]['long'] = convert_tuple_to_action_object(BUTTON_ENTITY_MAP[button_name]['long'])

    logger.debug(f"Created button entity map")
    return button_entity_map


def convert_tuple_to_action_object(map_item: tuple):
    dobiss_entities = get_entities(include_shade_relays=True)

    # If button is not configured, create no object
    if map_item is None:
        return None

    # If only the entity name is given, configure the default action "ACTION_SWITCH"
    elif type(map_item) is str:
        return EntityAction(target_entity=dobiss_entities[map_item], action=ACTION_SWITCH)

    # If an action_type is configured, pass it to the action object
    elif len(map_item) == 2:
        return EntityAction(target_entity=dobiss_entities[map_item[0]], action=map_item[1])

    # If an action_type and parameters are configured, pass them to the action object
    elif len(map_item) == 2:
        return EntityAction(target_entity=dobiss_entities[map_item[0]], action=map_item[1], named_arguments=map_item[2])

    else:
        raise NotImplementedError(f"Map item with {len(map_item)} elements is not supported. ({map_item})")


if __name__ == '__main__':
    dobiss_master()
