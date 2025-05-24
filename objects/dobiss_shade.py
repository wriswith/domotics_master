import time

from config.constants import SHADE, SHADE_STATE_UP, SHADE_COMMAND_DOWN, SHADE_STATE_GOING_UP, SHADE_COMMAND_UP, \
    SHADE_COMMAND_STOP, SHADE_STATE_DOWN, SHADE_STATE_STOPPED, SHADE_STATE_GOING_DOWN, SHADE_COMMAND_TOGGLE_UP, \
    SHADE_COMMAND_TOGGLE_DOWN
from logger import logger
from mqtt.mqtt_worker import MqttWorker
from objects.dobiss_entity import DobissEntity
from objects.dobiss_relay import DobissRelay


class DobissShade(DobissEntity):
    def __init__(self, name: str, relay_up: DobissRelay, relay_down: DobissRelay, speed_up, speed_down):
        super().__init__(SHADE, name)
        self.status = SHADE_STATE_DOWN
        self.relay_up = relay_up
        self.relay_down = relay_down
        self._position = 0
        self._last_calculation_time = time.time()  # Calculation needs to be run before every move command to have a consistent position.
        self.speed_up = speed_up  # % position change per second
        self.speed_down = speed_down  # % position change per second

    def __repr__(self):
        return super().__repr__() + (f" status: {self.status}, relay_up: {self.relay_up.current_status}, "
                                     f"relay_down: {self.relay_down.current_status}, _position {self._position}")

    @staticmethod
    def position_tracker(shades: dict):
        """
        Method to be run in separate thread to continuously track the position of each shade.
        :param shades:
        :return:
        """
        logger.debug(f"Tracking shade position for {len(shades)} shades. ({shades.keys()})")
        while True:
            for entity_name in shades:
                if shades[entity_name].status in (SHADE_STATE_GOING_DOWN, SHADE_STATE_GOING_UP):
                    shades[entity_name].update_position()
                    logger.debug(shades[entity_name])
            time.sleep(0.5)

    @property
    def position(self):
        self.update_position()
        return self._position

    def update_position(self):
        if self.status == SHADE_STATE_GOING_DOWN:

            logger.debug(f"time_dif {time.time() - self._last_calculation_time}")
            logger.debug(f"step {self.speed_down * (time.time() - self._last_calculation_time)}")

            self._position = int(self._position + (self.speed_down * (time.time() - self._last_calculation_time)))
            self._last_calculation_time = time.time()
            if self._position >= 100:
                self._position = 100
                self.status = SHADE_STATE_DOWN
                self.relay_down.set_status(0, force=True)
                self.relay_up.set_status(0, force=True)
            self.report_state_to_mqtt()
        elif self.status == SHADE_STATE_GOING_UP:

            logger.debug(f"time_dif {time.time() - self._last_calculation_time}")
            logger.debug(f"step {self.speed_up * (time.time() - self._last_calculation_time)}")

            self._position = int(self._position - (self.speed_up * (time.time() - self._last_calculation_time)))
            self._last_calculation_time = time.time()
            if self._position <= 0:
                self._position = 0
                self.status = SHADE_STATE_UP
                self.relay_down.set_status(0, force=True)
                self.relay_up.set_status(0, force=True)

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

        self._last_calculation_time = time.time()
        self.report_state_to_mqtt()

    def up(self):
        self.update_position()
        self.relay_up.set_status(1, force=True)
        self.status = SHADE_STATE_GOING_UP

    def down(self):
        self.update_position()
        self.relay_down.set_status(1, force=True)
        self.status = SHADE_STATE_GOING_DOWN

    def stop(self):
        self.update_position()
        self.relay_down.set_status(0, force=True)
        self.relay_up.set_status(0, force=True)
        self.status = SHADE_STATE_STOPPED
