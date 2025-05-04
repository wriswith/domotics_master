from can_bus_control import send_dobiss_command
from config.constants import DOBISS_DIMMER
from objects.dobiss_output import DobissOutput


class DobissDimmer(DobissOutput):
    def __init__(self, name: str, module_number: int, output: int):
        super().__init__(DOBISS_DIMMER, name, module_number, output)
        self.min_brightness = 0
        self.max_brightness = 100
        self.next_brightness_in_cycle = None
        self.cycle_direction = "down"

    def get_brightness_ratio(self):
        return (self.max_brightness - self.min_brightness) / 100

    def get_next_brightness_in_cycle(self):
        return int(self.next_brightness_in_cycle)

    def switch_status(self):
        if self.current_status == 0:
            self.set_status(1, self.max_brightness)
        else:
            self.set_status(0, 0)

    def set_status(self, new_status, new_brightness=100):
        if new_brightness > self.max_brightness:
            new_brightness = self.max_brightness
        self.current_status = new_status
        self.current_brightness = new_brightness
        if new_status == 0:
            self.next_brightness_in_cycle = None
        send_dobiss_command(self.module_id, self.get_msg_to_set_status(self.current_brightness))

    def cycle_brightness(self):
        step = 1 * self.get_brightness_ratio()

        # If first loop in cycle, initialize cycle
        if self.next_brightness_in_cycle is None:
            self.next_brightness_in_cycle = self.current_brightness + step

        # When going over max brightness, set to max and switch cycle direction
        if self.next_brightness_in_cycle >= self.max_brightness:
            self.set_status(1, self.max_brightness)
            self.cycle_direction = 'down'
            self.next_brightness_in_cycle -= step

        # When going over min brightness, switch direction
        elif self.next_brightness_in_cycle <= self.min_brightness:
            self.cycle_direction = 'up'
            self.set_status(1, self.min_brightness)
            self.next_brightness_in_cycle += step

        # Continue cycle in the requested direction
        else:
            self.set_status(1, int(self.next_brightness_in_cycle))
            if self.cycle_direction == 'down':
                self.next_brightness_in_cycle -= step
            else:
                self.next_brightness_in_cycle += step

