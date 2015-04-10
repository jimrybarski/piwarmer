from datetime import datetime
from itertools import cycle
import smbus
import time
import numpy as np
import logging
import redis
import json
import RPIO
from RPIO import PWM

log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


class Data(object):
    def __init__(self):
        self._conn = None

    @property
    def conn(self):
        return redis.StrictRedis()

    def update_temperature(self, temp):
        self.conn.set("current_temp", temp)

    def deactivate(self):
        self.conn.set("active", 0)

    def activate(self):
        self.conn.set("active", 1)

    @property
    def program(self):
        return self.conn.get("program")

    @property
    def active(self):
        return self.conn.get("active") == "1"


class Output(object):
    ENABLE_PIN = 27
    PWM_PIN = 28

    def __init__(self):
        RPIO.setup(RPIO.BOARD)
        RPIO.setup(Output.ENABLE_PIN, RPIO.OUT)
        RPIO.setup(Output.PWM_PIN, RPIO.OUT)
        # Sets up a PWM pin with 1 second cycles
        self._pwm = PWM.Servo(subcycle_time_us=1000000)

    def enable(self):
        RPIO.output(Output.ENABLE_PIN, True)

    def disable(self):
        RPIO.output(Output.ENABLE_PIN, False)

    def set_pwm(self, duty_cycle):
        assert 0.0 <= duty_cycle <= 1.0
        self._pwm.set_servo(Output.PWM_PIN, 1000000 * duty_cycle)


class TemperatureProbe(object):
    GPIO_ADDRESS = 0x4d

    def __init__(self):
        self._bus = smbus.SMBus(1)
        log.debug("Connected to SMBus")

    @property
    def current_temperature(self):
        data = self._bus.read_i2c_block_data(TemperatureProbe.GPIO_ADDRESS, 1, 2)
        return ((data[0] * 256) + data[1]) / 5.0


class TemperatureController(object):
    def __init__(self):
        self._probe = TemperatureProbe()
        self._data = Data()
        # Disable the temperature controller on boot to ensure we're not running an old program
        self._data.deactivate()
        self._program = None
        self._history_key = None

    def _update_temperature(self):
        temperature = self._probe.current_temperature
        log.debug("current_temp: %s" % temperature)
        self._data.update_temperature(temperature)

    def _run_program(self):
        while True:
            if not self._data.active:


    def _activate(self):
        self._program = TemperatureProgram()
        self._program.load_json(self._data.program)
        self._history_key = self._get_history_key()

    def _get_history_key(self):
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def run(self):
        while True:
            self._listen()
            self._run_program()

    def _listen(self):
        """
        Do nothing until someone instructs the temperature controller to start running.

        :return:
        """
        while True:
            if self._data.active:
                break
            else:
                log.debug("Temperature controller inactive.")
                time.sleep(1)


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

    def load_json(self, json_program):
        raw_program = json.loads(json_program)
        # TODO: Build up the temperature settings here

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