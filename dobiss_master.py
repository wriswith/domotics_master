from dobiss_entity import DobissEntity
from dobiss_entity_config import DOBISS_LIGHTS_CONFIG


def dobiss_master():
    dobiss_entities = generate_dobiss_entities()



def generate_dobiss_entities():
    dobiss_entities = {}
    for name in DOBISS_LIGHTS_CONFIG:
        dobiss_entities[name] = DobissEntity(DOBISS_LIGHTS_CONFIG[name], name)
    return dobiss_entities


if __name__ == '__main__':
    dobiss_master()
