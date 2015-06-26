class RoundData(object):
    def __init__(self, accumulated_error=0.0):
        self.accumulated_error = accumulated_error
        self.active = None
        self.desired_temperature = None
        self.duty_cycle = None
        self.driver = None
        self.mode = None
        self.program = None
        self.seconds_left = None
        self.start_time = None
        self.temperature = None
        self.current_time = None