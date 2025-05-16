from can_bus_control import send_dobiss_command
from config.constants import DOBISS_RELAY
from logger import logger
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_output import DobissOutput


class DobissRelay(DobissOutput):
    def __init__(self, name: str, module_number: int, output: int):
        super().__init__(DOBISS_RELAY, name, module_number, output)

    def switch_status(self):
        if self.current_status == 0:
            self.set_status(1)
        else:
            self.set_status(0)

    def report_state_to_mqtt(self):
        MqttWorker.get_mqtt_worker().publish_queue.put((self.get_mqtt_state_topic(), self.get_mqtt_status(), True))

    def set_status(self, new_status, brightness=100):
        if self.current_brightness == brightness and self.current_status == new_status:
            logger.debug(f"Ignoring status update for {self.name} because the new status equals the current status")
        else:
            self.current_status = new_status
            send_dobiss_command(self.module_id, self.get_msg_to_set_status())
            self.report_state_to_mqtt()
