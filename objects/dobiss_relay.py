from can_bus_control import send_dobiss_command
from config.constants import DOBISS_RELAY
from objects.dobiss_output import DobissOutput


class DobissRelay(DobissOutput):
    def __init__(self, name: str, module_number: int, output: int):
        super().__init__(DOBISS_RELAY, name, module_number, output)

    def switch_status(self):
        if self.current_status == 0:
            self.set_status(1)
        else:
            self.set_status(0)

    def set_status(self, new_status, brightness=100):
        self.current_status = new_status
        send_dobiss_command(self.module_id, self.get_msg_to_set_status())
