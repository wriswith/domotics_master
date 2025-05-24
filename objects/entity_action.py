import threading

from config.constants import *


class EntityAction:
    def __init__(self, target_entity, action: str, named_arguments: {} = None):
        self.target_entity = target_entity
        self.action = action
        self.named_arguments = named_arguments

    def execute(self):
        if self.action == ACTION_SWITCH:
            self.target_entity.switch_status()
        elif self.action == ACTION_TURN_ON:
            self.target_entity.set_status(1)
        elif self.action == ACTION_TURN_OFF:
            self.target_entity.set_status(0)
        elif self.action == ACTION_SCHEDULE:
            delay = self.named_arguments["delay"]
            real_action = self.named_arguments["real_action"]
            new_entity_action = EntityAction(self.target_entity, real_action, self.named_arguments["named_arguments"])
            threading.Timer(delay, EntityAction.execute, (new_entity_action, )).start()
        elif self.action == ACTION_CYCLE_DIMMER:
            self.target_entity.cycle_brightness()
        elif self.action in (SHADE_COMMAND_UP, SHADE_COMMAND_STOP, SHADE_COMMAND_DOWN, SHADE_COMMAND_TOGGLE_UP,
                             SHADE_COMMAND_TOGGLE_DOWN):
            self.target_entity.set_status(self.action)
        else:
            raise NotImplementedError(f"The action {self.action} is not implemented.")
