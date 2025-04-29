from config.dobiss_entity_config import DOBISS_SCENE
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relays import DobissRelays

SH

class DobissScene(DobissEntity):
    def __init__(self, name: str, relays_up: DobissRelays, relays_down: DobissRelays):
        super().__init__(DOBISS_SCENE, name)
        self.status = 'up'  # We are not able to determine the shade status from the module outputs. We assume up.

