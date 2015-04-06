from itertools import cycle
import smbus
import time
import numpy as np
import logging
import redis

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


class TemperatureController(object):
    def __init__(self):
        self._bus = smbus.SMBus(1)
        self._latest_temp = None

    def read_temperature(self):
        data = self._bus.read_i2c_block_data(0x4d, 1, 2)
        self._latest_temp = ((data[0] << 8) + data[1]) / 5.00
        redis.StrictRedis().set("current_temp", self._latest_temp)
        return self._latest_temp

    def run_program(self, program):
        pass


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
        self._looping = False
        self._start = None
        self._hold_temp = None

    def set_temperature(self, temperature, duration_in_seconds):
        if not self._looping:
            setting = TemperatureSetting(temperature, duration_in_seconds)
            self._settings.append(setting)
        return self

    def repeat(self, times):
        if not self._looping:
            new_settings = []
            for i in range(times):
                for action in self._settings:
                    new_settings.append(action)
            self._settings = new_settings
        return self

    def loop_forever(self):
        self._looping = True
        return self

    def hold(self, temperature):
        self._hold_temp = temperature
        return self

    def start(self):
        self._start = time.time()

    def get_current_temperature(self):
        if self._looping:
            settings = cycle(self._settings)
        else:
            settings = self._settings
        elapsed = time.time() - self._start
        for setting in settings:
            elapsed -= setting.duration
            if elapsed < 0:
                return setting.temperature
        # The program program is over or holding at a specified temperature.
        return self._hold_temp if self._hold_temp else False


class PID:
    def __init__(self, kp=1.0, ki=1.0, kd=1.0, accumulated_error_min=-20, accumulated_error_max=20):
        assert accumulated_error_min < 0 < accumulated_error_max
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._previous_errors = []
        self._accumulated_error = 0.0
        self._accumulated_error_max = accumulated_error_max
        self._accumulated_error_min = accumulated_error_min
        self._set_point = 25.0

    def update(self, current_value):
        log.debug("\n\n")
        error = self._set_point - current_value
        log.debug("Error: %s" % error)
        self._update_previous_errors(current_value, error)
        self._update_accumulated_error(error)
        p = self._kp * error
        log.debug("Proportional: %s" % p)
        i = self._accumulated_error * self._ki
        log.debug("Integral: %s" % i)
        d = self._calculate_error_derivative() * self._kd
        log.debug("Derivative: %s" % d)
        total = p + i + d
        log.debug("PID total: %s" % total)
        return total

    def _calculate_error_derivative(self):
        # finds the slope of the least squares regression for the last five error measurements
        a = np.vstack([np.array(self._previous_errors), np.ones(len(self._previous_errors))]).T
        b = np.arange(float(len(self._previous_errors)))
        slope = np.linalg.lstsq(a, b)[0][0]
        return slope

    def _update_previous_errors(self, current_value, error):
        if not self._previous_errors:
            self._previous_errors = [float(current_value) for i in range(5)]
        self._previous_errors.pop(0)
        self._previous_errors.append(error)

    def _update_accumulated_error(self, error):
        # Add the current error to the accumulated error
        self._accumulated_error += error
        # Ensure the value is within the allowed limits
        self._accumulated_error = min(self._accumulated_error, self._accumulated_error_max)
        self._accumulated_error = max(self._accumulated_error, self._accumulated_error_min)
        log.debug("Accumulated error: %s" % self._accumulated_error)

    @property
    def set_point(self):
        return self._set_point

    @set_point.setter
    def set_point(self, temperature):
        self._set_point = float(temperature)