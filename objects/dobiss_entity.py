from config.dobiss_entity_config import DOBISS_RELAY, DOBISS_DIMMER, DOBISS_MODULES


class DobissEntity:
    def __init__(self, module_number: int = None, output: int = None, dobiss_type: str = None, name: str = None):
        if module_number is None:
            raise ValueError(f"module_number can not be None.")
        if output is None:
            raise ValueError(f"output can not be None.")
        if dobiss_type not in (DOBISS_RELAY, DOBISS_DIMMER):
            raise ValueError(f"dobiss_type should be {DOBISS_RELAY} or {DOBISS_DIMMER} not {dobiss_type}.")
        self.module_number = module_number
        self.module_id = DOBISS_MODULES[module_number]['id']
        self.output = output
        self.dobiss_type = dobiss_type
        self.name = name
        self.current_status = None  # 0 = off, 1 = on
        self.current_brightness = 100  # for dimmers this represents the brightness and the max value is 100

    @staticmethod
    def config_to_dobiss_entity(config_dict, entity_name):
        """

        :param config_dict:
        :param entity_name:
        :return: DobissEntity
        """
        return DobissEntity(config_dict['module'], config_dict['output'], config_dict['dobiss_type'], entity_name)

    @staticmethod
    def shade_config_to_dobiss_entity(config_array, entity_name, action):
        """

        :param action:
        :param config_array:
        :param entity_name:
        :return: DobissEntity
        """
        return DobissEntity(config_array[f'output_{action}']['module'], config_array[f'output_{action}']['output'],
                            config_array['dobiss_type'], entity_name)

    @staticmethod
    def convert_name_to_entity_name(name):
        return name.replace(' ', '_').lower()

    @staticmethod
    def convert_int_to_hex(input_value: int):
        return input_value.to_bytes(1, 'big')

    def get_entity_name(self):
        return DobissEntity.convert_name_to_entity_name(self.name)

    def get_device_type_hex(self):
        if self.dobiss_type == DOBISS_RELAY:
            return b'\x08'
        elif self.dobiss_type == DOBISS_DIMMER:
            return b'\x10'
        elif self.dobiss_type == '0-10V':
            return b'\x18'
        else:
            raise ValueError(f"{self.dobiss_type} has no known device type hex")

    def get_module_hex(self):
        return self.module_number.to_bytes(1, 'big')

    def get_output_hex(self):
        return (self.output - 1).to_bytes(1, 'big')

    def get_full_address(self):
        return self.get_module_hex() + self.get_output_hex()

    def get_msg_to_set_status(self, status: int, brightness=100):
        self.current_status = status
        return (b'' + self.get_full_address() + self.current_status.to_bytes(1, 'big') + b'\xff\xff'
                + DobissEntity.convert_int_to_hex(brightness) + b'\xff\xff')

    def get_msg_to_switch_status(self):
        if self.dobiss_type == DOBISS_DIMMER:
            if self.current_status == 0:
                self.current_status = 2
                self.current_brightness = 100
            else:
                self.current_status = 0
        else:
            if self.current_status == 0:
                self.current_status = 1
            else:
                self.current_status = 0

        return (b'' + self.get_full_address() + DobissEntity.convert_int_to_hex(self.current_status) + b'\xff\xff'
                + DobissEntity.convert_int_to_hex(self.current_brightness) + b'\xff\xff')
