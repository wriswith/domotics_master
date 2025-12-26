from queue import Queue
from threading import Thread

from can_bus_control import get_modules_statuses
from config.button_entity_mapping import BUTTON_ENTITY_MAP
from config.config import ACTIVE_PICO_PINS
from config.constants import ACTION_SWITCH
from dobiss_entity_helper import get_entities, parse_module_status_response, get_entities_of_type
from logger import logger
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_entity import DobissEntity
from objects.dobiss_output import DobissOutput
from objects.dobiss_shade import DobissShade
from objects.entity_action import EntityAction
from one_wire_reader import one_wire_reader
from switch_event_handler import handle_switch_events


def dobiss_master():
    # Create the mapping between the buttons and the possible actions
    logger.debug("Creating button entity mapping.")
    button_entity_map = create_button_entity_map()

    # Read the current status of the entities from the modules using CAN bus
    logger.debug("Reading the status of the outputs of the modules")
    modules_statuses = get_modules_statuses()
    for module_number in modules_statuses:
        parse_module_status_response(modules_statuses[module_number], module_number)

    report_initial_state()

    # Start reading button events from the pico pi
    switch_event_queue = Queue()
    one_wire_reader(ACTIVE_PICO_PINS, switch_event_queue)

    MqttWorker.get_mqtt_worker().publish_discovery_topics(get_entities())

    # start_tracking_shades()

    # Execute the actions related to the button events
    handle_switch_events(switch_event_queue, button_entity_map)


# def start_tracking_shades():
#     shades = get_entities_of_type(DobissShade)
#     Thread(target=DobissShade.position_tracker, args=(shades,)).start()


def report_initial_state():
    logger.debug("Reporting the initial state of the outputs to MQTT.")
    entities = get_entities()
    for entity in entities:
        if isinstance(entity, DobissOutput):
            entity.report_state_to_mqtt()


def create_button_entity_map():
    """
    Create a dict with a key for every button name and as element the proper entity object to trigger upon short or long press.
    :return:
    """
    logger.debug(f"Creating button entity map")
    button_entity_map = {}
    for button_name in BUTTON_ENTITY_MAP:
        button_entity_map[button_name] = {}
        for key in BUTTON_ENTITY_MAP[button_name]:
            button_entity_map[button_name][key] = convert_tuple_to_action_object(BUTTON_ENTITY_MAP[button_name][key])

    logger.debug(f"Created button entity map")
    return button_entity_map


def convert_tuple_to_action_object(map_item: tuple):
    dobiss_entities = get_entities(include_shade_relays=True)

    # If button is not configured, create no object
    if map_item is None:
        return None

    # If only the entity name is given, configure the default action "ACTION_SWITCH"
    elif type(map_item) is str:
        target_entity_name = DobissEntity.convert_name_to_entity_name(map_item)
        return EntityAction(target_entity=dobiss_entities[target_entity_name], action=ACTION_SWITCH)

    target_entity = dobiss_entities[DobissEntity.convert_name_to_entity_name(map_item[0])]

    if len(map_item) == 1:
        return EntityAction(target_entity=target_entity, action=ACTION_SWITCH)

    # If an action_type is configured, pass it to the action object
    elif len(map_item) == 2:
        return EntityAction(target_entity=target_entity, action=map_item[1])

    # If an action_type and parameters are configured, pass them to the action object
    elif len(map_item) == 3:
        return EntityAction(target_entity=target_entity, action=map_item[1], named_arguments=map_item[2])

    else:
        raise NotImplementedError(f"Map item with {len(map_item)} elements is not supported. ({map_item})")


if __name__ == '__main__':
    dobiss_master()
