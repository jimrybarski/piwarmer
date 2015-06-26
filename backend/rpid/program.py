import json
import logging

log = logging.getLogger(__name__)


class TemperatureSetting(object):
    def __init__(self, temperature, duration_in_seconds):
        self._temperature = temperature
        self._duration = duration_in_seconds

    @property
    def temperature(self):
        return self._temperature

    @property
    def duration(self):
        return self._duration


class TemperatureProgram(object):
    def __init__(self):
        self._settings = []
        self._start = None
        self._hold_temp = None
        self._total_duration = 0.0

    def minutes_left(self, current_time):
        seconds_left = max(self._total_duration - current_time + self._start, 0)
        log.debug("seconds left: %s" % seconds_left)
        return int(seconds_left / 60.0)

    def load_json(self, json_program):
        """
        json_program will be a dict like:
        {
          "1": {"mode": "set", "temperature": 80.0, "duration": 300},
          "2": {"mode": "linear", "start_temperature": 80.0, "end_temperature": 37.0, "duration": 3600},
          "3": {"mode": "hold", "temperature": 37.0}
        }

        Modes and attributes supported:

        set: temperature, duration
        repeat: num_repeats
        hold: temperature
        linear: temperature, duration

        :param json_program:    temperature settings for an experiment
        :type json_program:     str

        """
        action = {"set": self.set_temperature,
                  "linear": self.linear,
                  "repeat": self.repeat,
                  "hold": self.hold
                  }
        raw_program = json.loads(json_program)
        for index, parameters in sorted(raw_program.items(), key=lambda x: int(x[0])):
            # Get the mode and remove it from the parameters
            mode = parameters.pop("mode", None)
            # Run the desired action using the parameters given
            # Parameters of methods must match the keys exactly!
            log.debug("Adding instruction: %s with parameters: %s" % (mode, parameters))
            action[mode](**parameters)

    def set_temperature(self, temperature=25.0, duration=60):
        setting = TemperatureSetting(float(temperature), int(duration))
        self._total_duration += int(duration)
        self._settings.append(setting)
        return self

    def linear(self, start_temperature=60.0, end_temperature=37.0, duration=3600):
        # at least one minute long, must be multiple of 15
        duration = int(duration)
        start_temperature = float(start_temperature)
        end_temperature = float(end_temperature)
        total_diff = start_temperature - end_temperature
        # Limit the granularity to 4 temperature changes per minute
        setting_count = int(max(1, duration / 15))
        step_diff = total_diff / setting_count
        temperature = start_temperature
        for _ in xrange(setting_count):
            temperature -= step_diff
            setting = TemperatureSetting(float(temperature), duration)
            self._total_duration += duration
            self._settings.append(setting)

    def repeat(self, num_repeats=3):
        new_settings = []
        for i in range(num_repeats):
            for action in self._settings:
                new_settings.append(action)
                self._total_duration += action.duration
        self._settings = new_settings
        return self

    def hold(self, temperature=25.0):
        self._hold_temp = temperature
        return self

    def start(self, current_time):
        assert self._start is None
        self._start = current_time

    def get_desired_temperature(self, current_time):
        elapsed = current_time - self._start
        for setting in self._settings:
            elapsed -= setting.duration
            if elapsed < 0:
                return float(setting.temperature)
        # The program program is over or holding at a specified temperature.
        return float(self._hold_temp) if self._hold_temp else False
