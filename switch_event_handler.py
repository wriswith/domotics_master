import time
import traceback

from config.config import BUTTON_LOCKOUT_PERIOD
from config.constants import SWITCH_ACTION_HOLD, SWITCH_ACTION_RELEASE, CLICK_MODE_SHORT, \
    BUTTON_SHORT_RELEASE, BUTTON_SHORT_INSTA, BUTTON_LONG_RELEASE, BUTTON_LONG_INSTA, SWITCH_ACTION_PRESS, \
    BUTTON_LONG_HOLD
from logger import logger
from objects.entity_action import EntityAction
from objects.switch_event import SwitchEvent


def check_for_lockouts(switch_event: SwitchEvent, switch_locked_out: str, lockout_timestamp: float):
    locked_out = False

    # If a specific button is locked out, it should be ignored until release. Release must clear the lock out.
    if switch_event.button_name == switch_locked_out:
        if switch_event.action == SWITCH_ACTION_HOLD:
            locked_out = True
        elif switch_event.action == SWITCH_ACTION_RELEASE:
            switch_locked_out = None
            locked_out = True
        else:
            switch_locked_out = None

    # Check if there is a general lockout on all buttons for a specific time
    if lockout_timestamp is not None:
        if time.time() < lockout_timestamp:
            logger.debug(f"Dropping a button in the lockout period.")
            locked_out = True
        else:
            lockout_timestamp = None

    return switch_locked_out, lockout_timestamp, locked_out


def handle_button_release(switch_event: SwitchEvent, button_entity_map):
    click_mode = switch_event.get_click_mode()

    # Translate the click mode to the relevant keys in the button_entity_map
    if click_mode == CLICK_MODE_SHORT:
        matching_keys = [BUTTON_SHORT_RELEASE, BUTTON_SHORT_INSTA]
    else:
        matching_keys = [BUTTON_LONG_RELEASE, BUTTON_LONG_INSTA]

    # Check for every relevant key if there is an action configured for this button
    for matching_key in matching_keys:
        if matching_key in button_entity_map[switch_event.button_name]:
            execute_action(button_entity_map[switch_event.button_name][matching_key], matching_key, switch_event.button_name)

    # ignore button presses for the next 0.2 seconds to avoid double releases
    return time.time() + BUTTON_LOCKOUT_PERIOD


def handle_button_hold(switch_event: SwitchEvent, button_entity_map):
    actions_linked_to_button = button_entity_map[switch_event.button_name]

    click_mode = switch_event.get_click_mode()

    # Translate the click mode to the relevant keys in the button_entity_map
    if click_mode == CLICK_MODE_SHORT:
        if BUTTON_SHORT_INSTA in actions_linked_to_button:
            execute_action(actions_linked_to_button[BUTTON_SHORT_INSTA], BUTTON_SHORT_INSTA, switch_event.button_name)
            return switch_event.button_name  # Lock this button until it is released
    else:
        if BUTTON_LONG_INSTA in actions_linked_to_button:
            execute_action(actions_linked_to_button[BUTTON_LONG_INSTA], BUTTON_LONG_INSTA, switch_event.button_name)
            return switch_event.button_name  # Lock this button until it is released
        elif BUTTON_LONG_HOLD in actions_linked_to_button:
            execute_action(actions_linked_to_button[BUTTON_LONG_INSTA], BUTTON_LONG_INSTA, switch_event.button_name)

    return None


def execute_action(entity_action: EntityAction, button_mode: str, button_name: str):
    try:
        logger.info(f"Executing action {entity_action.action} on {entity_action.target_entity.name} after "
                    f"{button_mode} click on {button_name}")
        entity_action.execute()
    except Exception as e:
        logger.error(f"Failed to switch {entity_action}: {e}")
        traceback.print_exc()


def handle_button_press(switch_event: SwitchEvent, button_entity_map):
    """
    If a button is just being pressed in, handle the insta action if it is defined.
    :param switch_event:
    :param button_entity_map:
    :return:
    """
    if BUTTON_SHORT_INSTA in button_entity_map[switch_event.button_name]:
        execute_action(button_entity_map[switch_event.button_name][BUTTON_SHORT_INSTA], BUTTON_SHORT_INSTA, switch_event.button_name)
        return switch_event.button_name
    return None


def handle_switch_events(switch_event_queue, button_entity_map):
    lockout_timestamp = None  # Variable to set an epoch before which all buttons should be ignored (to avoid double clicks)
    switch_locked_out = None
    while True:
        switch_event = switch_event_queue.get()
        try:

            # Check if any lock outs should be adhered
            switch_locked_out, lockout_timestamp, locked_out = check_for_lockouts(switch_event, switch_locked_out, lockout_timestamp)
            if locked_out:
                continue

            if switch_event.action == SWITCH_ACTION_PRESS:
                switch_locked_out = handle_button_press(switch_event, button_entity_map)

            elif switch_event.action == SWITCH_ACTION_HOLD:
                switch_locked_out = handle_button_hold(switch_event, button_entity_map)

            elif switch_event.action == SWITCH_ACTION_RELEASE:
                lockout_timestamp = handle_button_release(switch_event, button_entity_map)

            else:
                raise NotImplementedError(f'Unknown action ({switch_event.action})')

        except Exception as e:
            logger.error(f"Failed to switch {switch_event}: {e}")


