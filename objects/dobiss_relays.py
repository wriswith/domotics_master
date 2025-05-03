from can_bus_control import send_dobiss_command
from config.constants import DOBISS_RELAY
from objects.dobiss_entity import DobissEntity
from objects.dobiss_output import DobissOutput


class DobissRelays(DobissOutput):
    def __init__(self, name: str, module_number: int, output: int):
        super().__init__(DOBISS_RELAY, name, module_number, output)

    @staticmethod
    def config_to_dobiss_entity(config_dict, entity_name):
        """

        :param config_dict:
        :param entity_name:
        :return: DobissEntity
        """
        return DobissEntity(config_dict['module'], config_dict['output'], config_dict['dobiss_type'], entity_name)

    def switch_status(self):
        if self.current_status == 0:
            self.set_status(1)
        else:
            self.set_status(0)

    def set_status(self, new_status, brightness=100):
        self.current_status = new_status
        send_dobiss_command(self.module_id, self.get_msg_to_set_status())
