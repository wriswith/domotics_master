import time

from config.constants import SHADE, SHADE_STATE_OPEN, SHADE_COMMAND_CLOSE, SHADE_STATE_OPENING, SHADE_COMMAND_OPEN, \
    SHADE_COMMAND_STOP, SHADE_STATE_CLOSED, SHADE_STATE_STOPPED, SHADE_STATE_CLOSING, SHADE_COMMAND_TOGGLE_OPEN, \
    SHADE_COMMAND_TOGGLE_CLOSE
from logger import logger
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relay import DobissRelay


class DobissShade(DobissEntity):
    def __init__(self, name: str, relay_up: DobissRelay, relay_down: DobissRelay):
        super().__init__(SHADE, name)
        self.status = SHADE_STATE_CLOSED
        self.relay_up = relay_up
        self.relay_down = relay_down
        self._position = 0
        self._last_calculation_time = time.time()  # Calculation needs to be run before every move command to have a consistent position.
        self.speed = 10  # % position change per second

    def __repr__(self):
        return super().__repr__() + (f" status: {self.status}, relay_up: {self.relay_up.current_status}, "
                                     f"relay_down: {self.relay_down.current_status}, _position {self._position}")

    @staticmethod
    def position_tracker(shades):
        """
        Method to be run in separate thread to continuously track the position of each shade.
        :param shades:
        :return:
        """
        while True:
            for entity_name in shades:
                if shades[entity_name].status in (SHADE_STATE_CLOSING, SHADE_STATE_OPENING):
                    shades[entity_name].update_position()
                    logger.debug(shades[entity_name])
            time.sleep(0.5)

    @property
    def position(self):
        self.update_position()
        return self._position

    def update_position(self):
        if self.status == SHADE_STATE_CLOSING:
            self._position = int(self._position + (self.speed * (time.time() - self._last_calculation_time)))
            if self._position >= 100:
                self._position = 100
                self.status = SHADE_STATE_CLOSED
                self.relay_down.set_status(0, force=True)
                self.relay_up.set_status(0, force=True)
                self._last_calculation_time = time.time()
            self.report_state_to_mqtt()
        elif self.status == SHADE_STATE_OPENING:
            self._position = int(self._position - (self.speed * (time.time() - self._last_calculation_time)))
            if self._position <= 0:
                self._position = 0
                self.status = SHADE_STATE_OPEN
                self.relay_down.set_status(0, force=True)
                self.relay_up.set_status(0, force=True)
                self._last_calculation_time = time.time()
            self.report_state_to_mqtt()

    def get_mqtt_state_topic(self):
        return f"homeassistant/cover/{self.name}/state"

    def get_mqtt_position_topic(self):
        return f"homeassistant/cover/{self.name}/position"

    def get_mqtt_command_topic(self):
        return f"homeassistant/cover/{self.name}/set"

    def get_mqtt_set_position_topic(self):
        return f"homeassistant/cover/{self.name}/set_position"

    def get_discover_topic(self):
        return f"homeassistant/cover/{self.name}/config"

    def report_state_to_mqtt(self):
        publish_queue = MqttWorker.get_mqtt_worker().publish_queue
        publish_queue.put((self.get_mqtt_state_topic(), self.status, True))
        publish_queue.put((self.get_mqtt_position_topic(), self._position, True))

    def switch_status(self):
        if self.status in (SHADE_STATE_OPEN, SHADE_STATE_OPENING):
            self.set_status(SHADE_COMMAND_CLOSE)
        else:
            self.set_status(SHADE_STATE_OPEN)

    def set_status(self, command, brightness=100):
        if command == SHADE_COMMAND_OPEN:
            self.open()
        elif command == SHADE_COMMAND_CLOSE:
            self.close()
        elif command == SHADE_COMMAND_STOP:
            self.stop()
        elif command == SHADE_COMMAND_TOGGLE_OPEN:
            if self.status == SHADE_STATE_OPENING:
                self.stop()
            else:
                self.open()
        elif command == SHADE_COMMAND_TOGGLE_CLOSE:
            if self.status == SHADE_STATE_CLOSING:
                self.stop()
            else:
                self.close()
        else:
            raise Exception(f"Unknown command: {command}")

        self._last_calculation_time = time.time()
        self.report_state_to_mqtt()

    def open(self):
        self.update_position()
        self.relay_up.set_status(1, force=True)
        self.status = SHADE_STATE_OPENING

    def close(self):
        self.update_position()
        self.relay_down.set_status(1, force=True)
        self.status = SHADE_STATE_CLOSING

    def stop(self):
        self.update_position()
        self.relay_down.set_status(0, force=True)
        self.relay_down.set_status(0, force=True)
        self.status = SHADE_STATE_STOPPED
