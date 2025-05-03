from config.constants import SHADE
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relays import DobissRelays

SHADE_STATUS_UP = 'shade up'
SHADE_STATUS_DOWN = 'shade down'


class DobissShade(DobissEntity):
    def __init__(self, name: str, relays_up: DobissRelays, relays_down: DobissRelays):
        super().__init__(SHADE, name)
        self.status = None
        self.relays_up = relays_up
        self.relays_down = relays_down

    def get_msg_to_switch_status(self):
        if self.status == SHADE_STATUS_UP:
            self.status = SHADE_STATUS_DOWN
            self.relays_down.current_status = 1
            return self.relays_down.get_msg_to_set_status()
        else:
            self.status = SHADE_STATUS_UP
            self.relays_up.current_status = 1
            return self.relays_up.get_msg_to_set_status()

    def switch_status(self):
        if self.status == SHADE_STATUS_DOWN:
            self.set_status(SHADE_STATUS_UP)
        else:
            self.set_status(SHADE_STATUS_DOWN)

    def set_status(self, new_status, brightness=100):
        self.status = new_status
        if self.status == SHADE_STATUS_UP:
            self.relays_up.set_status(1)
        else:
            self.relays_down.set_status(1)
