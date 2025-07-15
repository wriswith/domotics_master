import threading
import time

from config.constants import SHADE, SHADE_STATE_UP, SHADE_COMMAND_DOWN, SHADE_STATE_GOING_UP, SHADE_COMMAND_UP, \
    SHADE_COMMAND_STOP, SHADE_STATE_STOPPED, SHADE_STATE_GOING_DOWN, SHADE_COMMAND_TOGGLE_UP, \
    SHADE_COMMAND_TOGGLE_DOWN, SHADE_STATE_DOWN
from logger import logger
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relay import DobissRelay
from objects.entity_action import EntityAction


class DobissShade(DobissEntity):
    def __init__(self, name: str, relay_up: DobissRelay, relay_down: DobissRelay, speed_up, speed_down):
        super().__init__(SHADE, name)
        self.status = SHADE_STATE_UP
        self.relay_up = relay_up
        self.relay_down = relay_down

    def __repr__(self):
        return super().__repr__() + (f" status: {self.status}, relay_up: {self.relay_up.current_status}, "
                                     f"relay_down: {self.relay_down.current_status}")

    def get_mqtt_state_topic(self):
        return f"homeassistant/cover/{self.name}/state"

    def get_mqtt_command_topic(self):
        return f"homeassistant/cover/{self.name}/set"

    def get_discover_topic(self):
        return f"homeassistant/cover/{self.name}/config"

    def report_state_to_mqtt(self):
        publish_queue = MqttWorker.get_mqtt_worker().publish_queue
        publish_queue.put((self.get_mqtt_state_topic(), self.status, True))

    def switch_status(self):
        if self.status in (SHADE_STATE_UP, SHADE_STATE_GOING_UP):
            self.set_status(SHADE_COMMAND_DOWN)
        else:
            self.set_status(SHADE_STATE_UP)

    def set_status(self, command, brightness=100):
        if command == SHADE_COMMAND_UP:
            self.up()
        elif command == SHADE_COMMAND_DOWN:
            self.down()
        elif command == SHADE_COMMAND_STOP:
            self.stop()
        elif command == SHADE_COMMAND_TOGGLE_UP:
            if self.status == SHADE_STATE_GOING_UP:
                self.stop()
            else:
                self.up()
        elif command == SHADE_COMMAND_TOGGLE_DOWN:
            if self.status == SHADE_STATE_GOING_DOWN:
                self.stop()
            else:
                self.down()
        else:
            raise Exception(f"Unknown command: {command}")

        self.report_state_to_mqtt()

    def up(self):
        self.relay_down.set_status(0, force=True)
        self.relay_up.set_status(1, force=True)
        self.status = SHADE_STATE_UP
        self.schedule_stop()
        self.report_state_to_mqtt()

    def down(self):
        self.relay_up.set_status(0, force=True)
        self.relay_down.set_status(1, force=True)
        self.status = SHADE_STATE_DOWN
        self.schedule_stop()
        self.report_state_to_mqtt()

    def stop(self):
        self.relay_down.set_status(0, force=True)
        self.relay_up.set_status(0, force=True)

    def schedule_stop(self, delay=15):
        threading.Timer(delay, EntityAction.execute, (EntityAction(self,
                                                                   SHADE_COMMAND_STOP),)).start()  # Reset switches when the screen is done moving.
