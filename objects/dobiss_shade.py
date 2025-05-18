from config.constants import SHADE, SHADE_STATE_OPEN, SHADE_COMMAND_CLOSE, SHADE_STATE_OPENING, SHADE_COMMAND_OPEN, \
    SHADE_COMMAND_STOP
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relay import DobissRelay



class DobissShade(DobissEntity):
    def __init__(self, name: str, relays_up: DobissRelay, relays_down: DobissRelay):
        super().__init__(SHADE, name)
        self.status = SHADE_STATE_OPEN
        self.relays_up = relays_up
        self.relays_down = relays_down

    def get_mqtt_state_topic(self):
        return f"homeassistant/cover/{self.name}/state"

    def get_mqtt_command_topic(self):
        return f"homeassistant/cover/{self.name}/set"

    def get_discover_topic(self):
        return f"homeassistant/cover/{self.name}/config"

    def report_state_to_mqtt(self):
        MqttWorker.get_mqtt_worker().publish_queue.put((self.get_mqtt_state_topic(), self.status, True))

    def switch_status(self):
        if self.status in (SHADE_STATE_OPEN, SHADE_STATE_OPENING):
            self.set_status(SHADE_COMMAND_CLOSE)
        else:
            self.set_status(SHADE_STATE_OPEN)

    def set_status(self, new_status, brightness=100):
        self.status = new_status
        if self.status == SHADE_COMMAND_OPEN:
            self.relays_up.set_status(1)
        elif self.status == SHADE_COMMAND_CLOSE:
            self.relays_down.set_status(1)
        elif self.status == SHADE_COMMAND_STOP:
            self.relays_down.set_status(0)
            self.relays_down.set_status(0)
        else:
            raise Exception(f"Unknown status: {new_status}")
