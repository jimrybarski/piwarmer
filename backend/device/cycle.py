class ProgramOver(Exception):
    """
    Signals that we have no more steps to run.

    """
    pass


class CurrentCycle(object):
    """
    A container for data about the current state of the program and the sensor data. A new one is created each second
    in the main loop and it is repopulated with fresh data each time.

    """
    def __init__(self):
        self.accumulated_error = None
        self.active = None
        self.current_time = None
        self.current_temperature = None
        self.duty_cycle = None
        self.program = None
        self.start_time = None

    def _get_current_setting(self):
        """
        Finds the setting that we should currently be using to calculate the target temperature.

        :return:    start time (in seconds), stop time (in seconds), the program setting
        :rtype:     int, int, ProgramSetting
        :raises:    ProgramOver

        """
        assert self.program is not None
        assert self.current_time is not None
        assert self.start_time is not None
        for start, stop, setting in self.steps:
            if stop is None or start <= self.seconds_elapsed < stop:
                # we're either at a Hold setting (stop is None) or we've found the current setting
                return start, stop, setting
        raise ProgramOver

    @property
    def current_step(self):
        """
        Gets the index of the current program setting.

        :rtype:     int

        """
        try:
            start, stop, setting = self._get_current_setting()
            return setting.index
        except ProgramOver:
            return None

    @property
    def desired_temperature(self):
        """
        Gets the target temperature for the current setting.

        :rtype:     float

        """
        try:
            start, stop, setting = self._get_current_setting()
            return setting.get_temperature(self.seconds_elapsed - start)
        except ProgramOver:
            return None

    @property
    def seconds_left(self):
        """
        The number of seconds until the program is over.

        :rtype:     int

        """
        assert self.program is not None
        assert self.current_time is not None
        assert self.start_time is not None
        return int(max(self.program.total_duration - self.seconds_elapsed, 0))

    @property
    def steps(self):
        """
        Yields program settings in order along with their start and stop times (in seconds from the start of the program).

        """
        for (start, stop), setting in sorted(self.program.settings.items()):
            yield start, stop, setting

    @property
    def seconds_elapsed(self):
        return (self.current_time - self.start_time).total_seconds()
