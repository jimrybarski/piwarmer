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
        return bool(self.desired_temperature) and self.current_temperature is not None

    @property
    def seconds_elapsed(self):
        return (self.current_time - self.start_time).total_seconds()
