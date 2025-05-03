import time
from typing import List

from config.dobiss_entity_config import DOBISS_SCENE
from objects.dobiss_entity import DobissEntity
from objects.entity_action import EntityAction


class DobissScene(DobissEntity):
    def __init__(self, name: str, action_list: List[EntityAction]):
        super().__init__(DOBISS_SCENE, name)
        self.action_list = action_list

    def set_status(self, new_status, brightness=100):
        if new_status != 1:
            raise Exception(f"A dobiss scene can only be switched on. (requested status: {new_status})")
        for action in self.action_list:
            action.execute()
            time.sleep(0.1)

    def switch_status(self):
        self.set_status(1)
