from config.dobiss_entity_config import DOBISS_MODULES
from objects.dobiss_entity import DobissEntity


class DobissOutput(DobissEntity):
    def __init__(self, dobiss_type: str, name: str, module_number: int, output_number: int):
        super().__init__(dobiss_type, name)
        self.module_number = module_number
        self.module_id = DOBISS_MODULES[module_number]['id']
        self.output_number = output_number
        self.current_status = None

    def __repr__(self):
        return super().__repr__() + f", M{self.module_number}/O{self.output_number}, status {self.current_status}"

    def get_output_hex(self):
        return (self.output_number - 1).to_bytes(1, 'big')

    def get_full_address(self):
        return self.get_module_hex() + self.get_output_hex()

    def get_module_hex(self):
        return self.module_number.to_bytes(1, 'big')

    def get_msg_to_set_status(self, brightness=100):
        return (b'' + self.get_full_address() + self.current_status.to_bytes(1, 'big') + b'\xff\xff'
                + DobissEntity.convert_int_to_hex(brightness) + b'\xff\xff')
