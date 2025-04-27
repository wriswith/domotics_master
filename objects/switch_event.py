from config.button_names_config import CIRCUIT_ID_BUTTON_MAPPING
from config.config import ALLOW_NEW_CIRCUIT_IDS

# action can be press, hold, release
SWITCH_ACTION_PRESS = 'press'
SWITCH_ACTION_HOLD = 'hold'
SWITCH_ACTION_RELEASE = 'release'


class SwitchEvent:
    def __init__(self, circuit_id, action, duration):
        self.circuit_id = circuit_id
        self.action = action
        self.duration = duration
        if circuit_id in CIRCUIT_ID_BUTTON_MAPPING:
            self.button_name = CIRCUIT_ID_BUTTON_MAPPING[circuit_id]
        else:
            if ALLOW_NEW_CIRCUIT_IDS:
                self.button_name = None
            else:
                raise Exception(f"Unknown circuit id should not have been parsed. ({circuit_id})")