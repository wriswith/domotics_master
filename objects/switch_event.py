

# action can be press, hold, release
SWITCH_ACTION_PRESS = 'press'
SWITCH_ACTION_HOLD = 'hold'
SWITCH_ACTION_RELEASE = 'release'


class SwitchEvent:
    def __init__(self, circuit_id, action, duration):
        self.circuit_id = circuit_id
        self.action = action
        self.duration = duration