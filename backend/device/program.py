import copy
import logging

log = logging.getLogger(__name__)


class TemperatureSetting(object):
    def __init__(self, index, start_temp, final_temp, duration):
        assert duration is None or duration > 0.0
        self.index = index
        self._start_temp = float(start_temp)
        self._final_temp = float(final_temp)
        self.duration = duration

    def get_temperature(self, seconds_into_setting):
        if self.duration is None:
            # Hold setting
            return self._start_temp
        # Set or Linear Gradient
        percentage_done = float(seconds_into_setting) / self.duration
        offset = (self._final_temp - self._start_temp) * percentage_done
        return self._start_temp + offset


class TemperatureProgram(object):
    def __init__(self, steps):
        self._settings = {}
        self._has_hold = False
        self._total_duration = 0.0
        self._load_program(steps)

    @property
    def settings(self):
        return self._settings

    @property
    def total_duration(self):
        return self._total_duration

    def _load_program(self, steps):
        """
        steps will be a dict like:
        {
          "0": {"mode": "set", "temperature": 80.0, "duration": "1:30:00"},
          "1": {"mode": "linear", "start_temperature": 80.0, "end_temperature": 37.0, "duration": "12:00"},
          "2": {"mode": "hold", "temperature": 37.0}
        }

        Modes and attributes supported:

        set: temperature, duration
        repeat: num_repeats
        hold: temperature
        linear: temperature, duration

        :param steps:    temperature settings for an experiment
        :type steps:     dict

        """
        action = {"set": self._set_temperature,
                  "linear": self._linear,
                  "repeat": self._repeat,
                  "hold": self._hold
                  }
        # Go through the list of steps, ordered by the integer value of the index (which is a string in the original JSON)
        for index, parameters in sorted(steps.items(), key=lambda x: int(x[0])):
            # Get the mode and remove it from the parameters
            mode = parameters.pop("mode")
            # Run the desired action using the parameters given
            # Parameters of methods must match the keys exactly!
            if not self._has_hold:
                action[mode](index, **parameters)

    def _hhmmss_to_seconds(self, text):
        if type(text) == int:
            return text
        seconds = 0
        multiplier = 1
        for val in text.split(':')[::-1]:
            seconds += int(val) * multiplier
            multiplier *= 60
        return seconds

    def _set_temperature(self, index, temperature=25.0, duration=60):
        temperature = float(temperature)
        duration = self._hhmmss_to_seconds(duration)
        setting = TemperatureSetting(index, temperature, temperature, duration)
        self._settings[(self._total_duration, self._total_duration + duration)] = setting
        self._total_duration += duration

    def _linear(self, index, start_temperature=60.0, end_temperature=37.0, duration=3600):
        duration = self._hhmmss_to_seconds(duration)
        setting = TemperatureSetting(index, float(start_temperature), float(end_temperature), duration)
        self._settings[(self._total_duration, self._total_duration + duration)] = setting
        self._total_duration += duration

    def _repeat(self, index, num_repeats=3):
        new_settings = []
        offset = 0
        for i in range(int(num_repeats)):
            for time_range, setting in sorted(self._settings.items()):
                new_setting = copy.copy(setting)
                new_setting.index = index + offset
                new_settings.append(new_setting)
                offset += 1
        for setting in new_settings:
            # The duration must be defined because otherwise it means there's a repeat after a hold - nonsensical
            assert setting.duration is not None
            self._settings[(self._total_duration, self._total_duration + setting.duration)] = setting
            self._total_duration += setting.duration

    def _hold(self, index, temperature=25.0):
        setting = TemperatureSetting(index, float(temperature), float(temperature), None)
        self._settings[(self._total_duration, None)] = setting
        self._has_hold = True
