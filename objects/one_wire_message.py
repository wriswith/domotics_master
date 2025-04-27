import re

from config.button_names_config import CIRCUIT_ID_BUTTON_MAPPING
from config.config import ALLOW_NEW_CIRCUIT_IDS

MT_HEARTBEAT = "heartbeat"
MT_INVALID = "invalid"
MT_CIRCUIT_ID = "circuit_id"


class OneWireMessage:
    def __init__(self, raw_message):
        """
        Two types of messages are possible: heartbeat (no slaves responded) or frame (a button was pressed)

        :param raw_message:
        """
        self.raw_message = raw_message
        if raw_message.startswith("--- Heartbeat"):
            groups = re.match(r"--- Heartbeat (\d+)_(\d+).*", raw_message)
            self.pin = int(groups.groups()[0])
            self.frame_number = int(groups.groups()[1])
            self.circuit_id = None
            self.message_type = MT_HEARTBEAT
        else:
            groups = re.match(r"--- Start frame (\d+)_(\d+): (([01]{8} ){8})", raw_message)
            if groups:
                self.pin = int(groups.groups()[0])
                self.frame_number = int(groups.groups()[1])
                self.circuit_id = groups.groups()[2].strip()
                if self.has_valid_circuit_id():
                    self.message_type = MT_CIRCUIT_ID
                else:
                    self.message_type = MT_INVALID
                    print(f"Dropping invalid circuit ID.")
            else:
                raise Exception(f"Unable to parse raw message: {raw_message}")

    def has_valid_circuit_id(self):
        """
        Check if circuit_id is valid by:
            - detecting an all zero circuit_id (happens when the bus is no longer powered)
            - bytes 6 and 7 are not 0, which all id's have.
            - an unknown circuit_id is detected and the config says this is not allowed.
        :return:
        """
        bytes = self.circuit_id.split(" ")
        if self.circuit_id == "00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000":
            print(f"All zero circuit_id, bus down? (pin: {self.pin})")
        if bytes[5] != "00000000" and bytes[6] != "00000000":
            print(f"Bytes 6 and 7 are not 0. ({self.circuit_id})")
            return False
        if self.circuit_id not in CIRCUIT_ID_BUTTON_MAPPING and not ALLOW_NEW_CIRCUIT_IDS:
            print(f"Unknown circuit id detected: {self.circuit_id}")
            return False
        return True

    def get_button_label(self):
        """
        Translate the circuit id to the user-friendly name.
        :return:
        """
        if self.circuit_id in CIRCUIT_ID_BUTTON_MAPPING:
            return CIRCUIT_ID_BUTTON_MAPPING[self.circuit_id]
        else:
            return self.circuit_id

    def circuit_id_is_known(self):
        """
        Check if the circuit_id is known in the config file
        :return:
        """
        return self.circuit_id in CIRCUIT_ID_BUTTON_MAPPING

    def circuit_id_is_unknown(self):
        """
        Check if the circuit_id is unknown in the config file
        :return:
        """
        return not self.circuit_id_is_known()
