DOBISS_RELAY = 'relay'
DOBISS_DIMMER = 'dimmer'
DOBISS_SCENE = 'scene'
DOBISS_SHADE = 'shade'
LIGHT = 'light'
VENTILATION = 'fan'
SHADE = 'cover'

SHADE_COMMAND_OPEN = 'OPEN'
SHADE_COMMAND_STOP = 'STOP'
SHADE_COMMAND_CLOSE = 'CLOSE'
SHADE_COMMAND_TOGGLE_OPEN = 'TOGGLE_OPEN'
SHADE_COMMAND_TOGGLE_CLOSE = 'TOGGLE_CLOSE'

SHADE_STATE_CLOSED = 'closed'
SHADE_STATE_CLOSING = 'closing'
SHADE_STATE_OPEN = 'open'
SHADE_STATE_OPENING = 'opening'
SHADE_STATE_STOPPED = 'stopped'

ACTION_SWITCH = 'switch'
ACTION_TURN_ON = 'turn_on'
ACTION_TURN_OFF = 'turn_off'
ACTION_SET_STATUS = 'set_status'
ACTION_SCHEDULE = 'schedule'
ACTION_CALL_FUNCTION = 'call_function'
ACTION_CYCLE_DIMMER = 'cycle_dimmer'

BUTTON_SHORT_RELEASE = 'short_release'  # Trigger when released before the SHORT_PRESS_CUTOFF. Should be combined with long trigger for this button.
BUTTON_SHORT_INSTA = 'short_insta'      # Trigger upon first press, must be only trigger for this button
BUTTON_LONG_RELEASE = 'long_release'    # Trigger when released after the SHORT_PRESS_CUTOFF.
BUTTON_LONG_HOLD = 'long_hold'          # Trigger continuously when held after the SHORT_PRESS_CUTOFF.
BUTTON_LONG_INSTA = 'long_insta'        # Trigger immediately when the SHORT_PRESS_CUTOFF timer is reached.

SWITCH_ACTION_PRESS = 'press'           # When a new circuit_id is detected, it causes a switch event "PRESS"
SWITCH_ACTION_HOLD = 'hold'             # Subsequential events with this circuit_id will cause events of the type "HOLD"
SWITCH_ACTION_RELEASE = 'release'       # When either no circuit_id or another circuit_id is detected, a RELEASE is triggered on the previous circuit_id.

CLICK_MODE_LONG = 'CLICK_MODE_LONG'     # The button has been pressed for longer than the SHORT_PRESS_CUTOFF
CLICK_MODE_SHORT = 'CLICK_MODE_SHORT'   # The button has been pressed for less or equal than the SHORT_PRESS_CUTOFF
