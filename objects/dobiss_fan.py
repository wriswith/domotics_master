import json
from typing import Dict

from config.constants import VENTILATION
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relay import DobissRelay


class DobissFan(DobissEntity):
    def __init__(self, dobiss_type: str, name: str, main_relay: DobissRelay, presets: Dict):
        super().__init__(dobiss_type, name)
        self.main_relay = main_relay
        self.current_status = 1
        self.device_type = VENTILATION
        self.available_presets = ["normal"]
        self.available_presets.extend(list(presets.keys()))
        self.current_preset = "normal"
        self.presets = presets

    @property
    def current_status(self):
        return self.main_relay.current_status

    @current_status.setter
    def current_status(self, value):
        self.main_relay.set_status(value)

    def __repr__(self):
        return super().__repr__() + f", M{self.main_relay.module_number}/O{self.main_relay.output_number}, status {self.current_status}, preset: {self.get_current_preset()}"

    def get_mqtt_state_topic(self):
        return f"homeassistant/fan/{self.name}/state"

    def get_mqtt_preset_state_topic(self):
        return f"homeassistant/fan/{self.name}/preset/state"

    def get_mqtt_command_topic(self):
        return f"homeassistant/fan/{self.name}/set"

    def get_mqtt_preset_command_topic(self):
        return f"homeassistant/fan/{self.name}/preset/set"

    def get_discover_topic(self):
        return f"homeassistant/fan/{self.name}/config"

    def get_preset_modes(self):
        return self.available_presets

    def get_mqtt_status(self):
        return self.main_relay.current_status

    def get_mqtt_preset_status(self):
        return self.get_current_preset()

    def switch_status(self):
        self.main_relay.switch_status()

    def report_state_to_mqtt(self):
        MqttWorker.get_mqtt_worker().publish_queue.put((self.get_mqtt_state_topic(), self.get_mqtt_status(), True))
        MqttWorker.get_mqtt_worker().publish_queue.put((self.get_mqtt_preset_state_topic(), self.get_mqtt_preset_status(), True))

    def get_current_preset(self):
        for preset in self.presets:
            if self.presets[preset].current_status == 1:
                return preset
        return "normal"

    def set_status(self, new_status, brightness=100, force=False):
        # reset the preset to normal when the fan is turned off
        if new_status == 0:
            self.set_preset("normal")

        # control the fan through the main fan relay
        self.main_relay.set_status(new_status)

    def set_preset(self, new_preset):
        for preset in self.presets:
            if new_preset != preset:
                self.presets[preset].set_status(0)
        if new_preset != "normal":
            self.presets[new_preset].set_status(1)
