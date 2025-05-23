import json

from can_bus_control import send_dobiss_command
from config.constants import DOBISS_DIMMER
from logger import logger
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_output import DobissOutput


class DobissDimmer(DobissOutput):
    def __init__(self, name: str, module_number: int, output: int, min_brightness=1, max_brightness=100):
        super().__init__(DOBISS_DIMMER, name, module_number, output)
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.next_brightness_in_cycle = min_brightness

    def __repr__(self):
        return super().__repr__() + (f", min/max brightness {self.min_brightness}/{self.max_brightness}, "
                                     f"(next brightness: {self.next_brightness_in_cycle})")

    def get_brightness_ratio(self):
        return (self.max_brightness - self.min_brightness) / 100

    def switch_status(self):
        if self.current_status == 0:
            self.set_status(1, self.max_brightness)
        else:
            self.set_status(0, 0)

    def get_mqtt_status(self):
        if self.current_status == 1:
            result = {"state": "ON"}
        else:
            result = {"state": "OFF"}
        result["brightness"] = self.current_brightness
        return json.dumps(result)

    def report_state_to_mqtt(self):
        MqttWorker.get_mqtt_worker().publish_queue.put((self.get_mqtt_state_topic(), self.get_mqtt_status(), True))

    def set_status(self, new_status, new_brightness=100):
        if self.current_brightness == new_brightness and self.current_status == new_status:
            logger.debug(f"Ignoring status update for {self.name} because the new status equals the current status")
        else:
            if new_brightness > self.max_brightness:
                new_brightness = self.max_brightness
            self.current_status = new_status
            self.current_brightness = new_brightness
            if new_status == 0:
                self.next_brightness_in_cycle = self.min_brightness
            logger.debug(f"Setting status of {self.name} to {new_status} (brightness={new_brightness})")
            send_dobiss_command(self.module_id, self.get_msg_to_set_status(self.current_brightness))
            self.report_state_to_mqtt()

    def cycle_brightness(self):
        step = 1 * self.get_brightness_ratio()

        # If first loop in cycle, initialize cycle
        if self.next_brightness_in_cycle is None:
            self.next_brightness_in_cycle = self.min_brightness

        self.set_status(1, int(self.next_brightness_in_cycle))

        # When going over max brightness, set to max and switch cycle direction
        if self.next_brightness_in_cycle >= self.max_brightness:
            self.next_brightness_in_cycle = self.min_brightness

        # Continue cycle in the requested direction
        else:
            self.next_brightness_in_cycle += step

