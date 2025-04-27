

class DobissModule:
    def __init__(self, module_number: int, module_type: str, module_can_id: int, nr_response_messages: int):
        self.module_number = module_number
        self.module_type = module_type
        self.module_can_id = module_can_id
        self.nr_response_messages = nr_response_messages

    @staticmethod
    def config_to_dobiss_module(config_dict):
        """

        :param config_dict:
        :return: DobissModule
        """
        return DobissModule(
            config_dict['module_number'],
            config_dict['type'],
            config_dict['id'],
            config_dict['nr_response_messages']
        )

    def get_status_msg(self):
        return bytes([self.module_number, 0xff])

    def get_status_can_id(self):
        return self.module_can_id - 1

