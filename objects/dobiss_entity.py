from config.constants import DOBISS_RELAY, DOBISS_DIMMER


class DobissEntity:
    def __init__(self, dobiss_type: str = None, name: str = None):
        self.dobiss_type = dobiss_type
        self.name = name
        self.current_brightness = 100  # for dimmers this represents the brightness and the max value is 100

    def __repr__(self):
        return f"DobissEntity: {self.dobiss_type}/{self.name}, brightness {self.current_brightness}"

    @staticmethod
    def convert_name_to_entity_name(name):
        return name.replace(' ', '_').lower()

    @staticmethod
    def convert_int_to_hex(input_value: int):
        return input_value.to_bytes(1, 'big')

    def get_entity_name(self):
        return DobissEntity.convert_name_to_entity_name(self.name)

    def get_mqtt_name(self):
        return f"mqtt_{self.get_entity_name()}"

    def get_mqtt_state_topic(self):
        return f"homeassistant/light/{self.get_mqtt_name()}/state"

    def set_status(self, new_status, brightness=100):
        raise NotImplementedError(f"This method needs to be overridden by child classes. ({self})")

    def switch_status(self):
        raise NotImplementedError(f"This method needs to be overridden by child classes. ({self})")

    def cycle_brightness(self):
        raise NotImplementedError(f"This method needs to be overridden by relevant child classes. ({self})")

    def get_device_type_hex(self):
        if self.dobiss_type == DOBISS_RELAY:
            return b'\x08'
        elif self.dobiss_type == DOBISS_DIMMER:
            return b'\x10'
        elif self.dobiss_type == '0-10V':
            return b'\x18'
        else:
            raise ValueError(f"{self.dobiss_type} has no known device type hex")
