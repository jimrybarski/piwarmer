class ProgramOverError(Exception):
    # No more steps left to run
    pass


class CurrentCycle(object):
    def __init__(self):
        self.accumulated_error = None
        self.active = None
        self.current_time = None
        self.current_temperature = None
        self.duty_cycle = None
        self.program = None
        self.start_time = None

    def _get_current_setting(self):
        assert self.program is not None
        assert self.current_time is not None
        assert self.start_time is not None
        for start, stop, setting in self.steps:
            if stop is None or start <= self.seconds_elapsed < stop:
                # we're either at a Hold setting (stop is None) or we've found the current setting
                return start, stop, setting
        raise ProgramOverError

    @property
    def current_step(self):
        try:
            start, stop, setting = self._get_current_setting()
            return setting.index
        except ProgramOverError:
            return None

    @property
    def desired_temperature(self):
        try:
            start, stop, setting = self._get_current_setting()
            return float(setting.get_temperature(self.seconds_elapsed - start))
        except ProgramOverError:
            return None

    @property
    def seconds_left(self):
        assert self.program is not None
        assert self.current_time is not None
        assert self.start_time is not None
        return int(max(self.program.total_duration - self.seconds_elapsed, 0))

    @property
    def steps(self):
        for (start, stop), setting in sorted(self.program.settings.items()):
            yield start, stop, setting

    @property
    def can_update_pid(self):
        return self.desired_temperature is not None

    @property
    def seconds_elapsed(self):
        return (self.current_time - self.start_time).total_seconds()
