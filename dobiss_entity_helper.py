from config.dobiss_entity_config import DOBISS_LIGHTS_CONFIG, DOBISS_SHADES_CONFIG, \
    DOBISS_SCENES_CONFIG, DOBISS_MODULES
from config.constants import DOBISS_RELAY, DOBISS_DIMMER
from objects.dobiss_dimmer import DobissDimmer
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relay import DobissRelay
from objects.dobiss_scene import DobissScene
from objects.dobiss_shade import DobissShade
from objects.entity_action import EntityAction

_entities = None
_entities_including_shade_relays = None


def get_entities(include_shade_relays=False):
    global _entities, _entities_including_shade_relays
    if _entities is None:
        _entities, _entities_including_shade_relays = generate_entities_from_config()

    if include_shade_relays:
        return _entities_including_shade_relays
    else:
        return _entities


def generate_entities_from_config():
    entities = {}
    shade_relay_entities = []
    for entity_name in DOBISS_LIGHTS_CONFIG:
        entity_config = DOBISS_LIGHTS_CONFIG[entity_name]
        if entity_config['dobiss_type'] == DOBISS_DIMMER:
            # read optional min/max brightness parameters
            if "min_brightness" in entity_config:
                min_brightness = entity_config['min_brightness']
            else:
                min_brightness = 1
            if "max_brightness" in entity_config:
                max_brightness = entity_config['max_brightness']
            else:
                max_brightness = 100

            entities[entity_name] = DobissDimmer(entity_name, entity_config['module'], entity_config['output'],
                                                 min_brightness, max_brightness)
        elif entity_config['dobiss_type'] == DOBISS_RELAY:
            entities[entity_name] = DobissRelay(entity_name, entity_config['module'], entity_config['output'])
        else:
            NotImplementedError()

    for shade_name in DOBISS_SHADES_CONFIG:
        shade_config = DOBISS_SHADES_CONFIG[shade_name]
        shade_up_entity = DobissRelay(f"{shade_name}_up", shade_config["output_up"]['module'],
                                      shade_config["output_up"]['output'])
        shade_down_entity = DobissRelay(f"{shade_name}_down", shade_config["output_down"]['module'],
                                        shade_config["output_down"]['output'])
        entities[shade_name] = DobissShade(shade_name, shade_up_entity, shade_down_entity)
        shade_relay_entities.extend((shade_up_entity, shade_down_entity))

    for scene_name in DOBISS_SCENES_CONFIG:
        action_list = []
        for entity_tuple in DOBISS_SCENES_CONFIG[scene_name]:
            if len(entity_tuple) == 2:
                action_list.append(EntityAction(entities[entity_tuple[0]], entity_tuple[1]))
            else:
                action_list.append(EntityAction(entities[entity_tuple[0]], entity_tuple[1], entity_tuple[2]))
        entities[scene_name] = DobissScene(scene_name, action_list)

    entities_including_shade_relays = entities.copy()
    for shade_relay_entity in shade_relay_entities:
        entities_including_shade_relays[shade_relay_entity.name] = shade_relay_entity

    return entities, entities_including_shade_relays


def get_output_list():
    entities = get_entities(include_shade_relays=True)
    result = []
    for entity_name, entity in entities.items():
        if entity.dobiss_type in (DOBISS_RELAY, DOBISS_DIMMER):
            result.append(entity)
    return result


def get_output_dict(key: str = 'module'):
    output_list = get_output_list()
    output_dict = {}
    if key == 'module':
        for module_number in DOBISS_MODULES:
            output_dict[module_number] = {}
        for entity in output_list:
            output_dict[entity.module_number][entity.output_number] = entity
    elif key == 'name':
        for entity in output_list:
            output_dict[entity.name] = entity
    else:
        raise NotImplementedError(f"{key} is not implemented.")
    return output_dict


def parse_module_status_response(response: bytes, module_number: int):
    """
    Parse the response of a module to the status of the individual outputs.
    :param response:
    :param module_number:
    :return:
    """
    output_dict = get_output_dict(key='module')
    output_number = 0
    for response_byte in response:
        if response_byte == 0xff:
            break  # no more outputs
        else:
            output_number += 1
            if output_number in output_dict[module_number]:
                entity = output_dict[module_number][output_number]
                if entity.dobiss_type == DOBISS_DIMMER:
                    if response_byte == 0:
                        entity.current_status = 0
                        entity.current_brightness = 0
                    else:
                        entity.current_status = 1
                        entity.current_brightness = response_byte
                else:
                    entity.current_status = response_byte
