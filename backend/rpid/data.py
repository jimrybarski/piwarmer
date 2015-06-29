import math


class RoundData(object):
    def __init__(self):
        self.accumulated_error = None
        self.active = None
        self.current_temperature = None
        self.desired_temperature = None
        self.duty_cycle = None
        self.program = None
        self.seconds_left = None
        self.start_time = None
        self.current_time = None

    @property
    def can_update_pid(self):
        return self.desired_temperature is not None and self.current_temperature is not None
