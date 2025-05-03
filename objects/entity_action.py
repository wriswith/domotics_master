from objects.dobiss_entity import DobissEntity




class EntityAction:
    def __init__(self, target_entity: DobissEntity, action: str, named_arguments: {} = None):
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
        else:
            raise NotImplementedError(f"The action {self.action} is not implemented.")
