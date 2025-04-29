from config.dobiss_entity_config import DOBISS_LIGHTS_CONFIG, DOBISS_DIMMER, DOBISS_RELAY, DOBISS_SHADES_CONFIG, \
    DOBISS_SCENE, DOBISS_SCENES_CONFIG
from objects.dobiss_dimmer import DobissDimmer
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relays import DobissRelays
from objects.dobiss_scene import DobissScene
from objects.dobiss_shade import DobissShade


def generate_entities():
    entities = {}
    for entity_name in DOBISS_LIGHTS_CONFIG:
        entity_config = DOBISS_LIGHTS_CONFIG[entity_name]
        if entity_config['dobiss_type'] == DOBISS_DIMMER:
            entities[entity_name] = DobissDimmer(entity_name, entity_config['module'], entity_config['output'])
        elif entity_config['dobiss_type'] == DOBISS_RELAY:
            entities[entity_name] = DobissRelays(entity_name, entity_config['module'], entity_config['output'])
        else:
            NotImplementedError()

    for shade_name in DOBISS_SHADES_CONFIG:
        shade_config = DOBISS_SHADES_CONFIG[shade_name]
        shade_up_entity = DobissRelays(shade_name, shade_config["output_up"]['module'], shade_config["output_up"]['output'])
        shade_down_entity = DobissRelays(shade_name, shade_config["output_down"]['module'], shade_config["output_down"]['output'])
        entities[shade_name] = DobissShade(shade_name, shade_up_entity, shade_down_entity)

    for scene_name in DOBISS_SCENES_CONFIG:
        dobiss_entities_and_status_list = []
        for entity_tuple in DOBISS_SCENES_CONFIG[scene_name]:
            dobiss_entities_and_status_list.append((entities[entity_tuple[0]], entity_tuple[1]))
        entities[scene_name] = DobissScene(scene_name, dobiss_entities_and_status_list)
    return entities


def parse_module_status_response(response: bytes, dobiss_entities, module_number: int):
    """
    Parse the response of a module to the status of the individual outputs.
    :param response:
    :param dobiss_entities:
    :param module_number:
    :return:
    """
    output_number = 0
    for response_byte in response:
        if response_byte == 0xff:
            break  # no more outputs
        else:
            output_number += 1
            if output_number in dobiss_entities[module_number]:
                entity = dobiss_entities[module_number][output_number]
                if entity.dobiss_type == DOBISS_DIMMER:
                    if response_byte == 0:
                        entity.current_status = 0
                        entity.current_brightness = 0
                    else:
                        entity.current_status = 1
                        entity.current_brightness = response_byte
                else:
                    dobiss_entities[module_number][output_number].current_status = response_byte