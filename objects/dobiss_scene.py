from typing import List

from config.dobiss_entity_config import DOBISS_SCENE
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relays import DobissRelays


class DobissScene(DobissEntity):
    def __init__(self, name: str, dobiss_entities_and_status_list: List[tuple]):
        super().__init__(DOBISS_SCENE, name)
        self.dobiss_entities_and_status_list = dobiss_entities_and_status_list

    def set_status(self, new_status, brightness=100):
        if new_status != 1:
            raise Exception(f"A dobiss scene can only be switched on. (requested status: {new_status})")
        for entity, status_tuple in self.dobiss_entities_and_status_list:
            if len(status_tuple) == 1:
                entity.set_status(status_tuple[0])
            else:
                entity.set_status(status_tuple[0], status_tuple[1])

    def switch_status(self):
        self.set_status(1)
