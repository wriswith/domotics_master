from can_bus_control import send_dobiss_command
from config.dobiss_entity_config import DOBISS_DIMMER
from objects.dobiss_output import DobissOutput


class DobissDimmer(DobissOutput):
    def __init__(self, name: str, module_number: int, output: int):
        super().__init__(DOBISS_DIMMER, name, module_number, output)

    def switch_status(self):
        if self.current_status == 0:
            self.set_status(1, 100)
        else:
            self.set_status(0, 0)

    def set_status(self, new_status, new_brightness=100):
        self.current_status = new_status
        self.current_brightness = new_brightness
        send_dobiss_command(self.module_id, self.get_msg_to_set_status(self.current_brightness))
