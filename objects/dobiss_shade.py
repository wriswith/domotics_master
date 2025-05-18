from config.constants import SHADE, SHADE_STATE_OPEN, SHADE_COMMAND_CLOSE, SHADE_STATE_OPENING, SHADE_COMMAND_OPEN, \
    SHADE_COMMAND_STOP, SHADE_STATE_CLOSED, SHADE_STATE_STOPPED
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relay import DobissRelay



class DobissShade(DobissEntity):
    def __init__(self, name: str, relay_up: DobissRelay, relay_down: DobissRelay):
        super().__init__(SHADE, name)
        self.status = SHADE_STATE_OPEN
        self.relay_up = relay_up
        self.relay_down = relay_down

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

    def set_status(self, command, brightness=100):
        if command == SHADE_COMMAND_OPEN:
            self.relay_up.set_status(1)
            self.status = SHADE_STATE_OPEN
        elif command == SHADE_COMMAND_CLOSE:
            self.relay_down.set_status(1)
            self.status = SHADE_STATE_CLOSED
        elif command == SHADE_COMMAND_STOP:
            self.relay_down.set_status(0)
            self.relay_down.set_status(0)
            self.status = SHADE_STATE_STOPPED
        else:
            raise Exception(f"Unknown command: {command}")

        self.report_state_to_mqtt()