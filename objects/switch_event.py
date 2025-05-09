from config.button_names_config import CIRCUIT_ID_BUTTON_MAPPING
from config.config import ALLOW_NEW_CIRCUIT_IDS, SHORT_PRESS_CUTOFF
from config.constants import CLICK_MODE_LONG, CLICK_MODE_SHORT


class SwitchEvent:
    """
    Object to communicate a button press, hold or release with the necessary metadata.
    """
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

    def get_click_mode(self):
        if self.duration > SHORT_PRESS_CUTOFF:
            return CLICK_MODE_LONG
        else:
            return CLICK_MODE_SHORT
