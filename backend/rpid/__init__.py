from datetime import datetime
import json
import logging
from logging import handlers
import redis
import smbus
import time
import Adafruit_MAX31855.MAX31855 as MAX31855


log = logging.getLogger()
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

TEN_MINUTES = 600


try:
    import RPi.GPIO as GPIO
except (SystemError, ImportError):
    log.warn("Not running on Raspberry Pi, GPIO cannot be imported.")


class Data(redis.StrictRedis):
    def update_temperature(self, temp):
        self.set("current_temp", temp)
        if self.llen("history") > TEN_MINUTES:
            self.lpop("history")
        self.rpush("history", temp)

    def update_setting(self, desired_temp):
        self.set("current_setting", desired_temp)

    def deactivate(self):
        self.set("active", 0)
        self.delete("program")

    def activate(self):
        self.set("active", 1)

    def save_data(self):
        """ Persists all data to disk asynchronously. """
        self.save()

    @property
    def program(self):
        return self.get("program")

    def set_program(self, program):
        self.set("program", json.dumps(program))

    @property
    def active(self):
        return self.get("active") == "1"

    @property
    def current_temp(self):
        return self.get("current_temp")

    @property
    def current_setting(self):
        return self.get("current_setting")

    def set_mode(self, mode):
        self.set("mode", mode)

    @property
    def manual(self):
        return self.get("mode") == "manual"

    @property
    def minutes_left(self):
        return self.get("minutes_left")

    @minutes_left.setter
    def minutes_left(self, value):
        self.set("minutes_left", value)

    @property
    def history(self):
        # gets the last ten minutes of temperature records
        return self.lrange("history", 0, -1)


class Output(object):
    PWM_PIN = 36
    ENABLE_PIN = 38
    HERTZ = 1.0  # the response is super slow so 1 Hz is fine

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(Output.ENABLE_PIN, GPIO.OUT)
        GPIO.setup(Output.PWM_PIN, GPIO.OUT)

    def enable(self):
        GPIO.output(Output.ENABLE_PIN, GPIO.HIGH)

    def disable(self):
        try:
            GPIO.output(Output.ENABLE_PIN, GPIO.LOW)
            GPIO.output(Output.PWM_PIN, GPIO.LOW)
        except:
            log.critical("DANGER! COULD NOT DEACTIVATE HEATER! UNPLUG IT IMMEDIATELY!")

    def set_pwm(self, new_duty_cycle):
        assert 0.0 <= new_duty_cycle <= 100.0
        log.info("duty cycle: %s" % new_duty_cycle)
        on_time = Output.HERTZ * new_duty_cycle / 100.0
        off_time = Output.HERTZ - on_time
        GPIO.output(Output.PWM_PIN, GPIO.HIGH)
        log.debug("PWM ON +++")
        time.sleep(on_time)
        GPIO.output(Output.PWM_PIN, GPIO.LOW)
        log.debug("PWM OFF ---")
        time.sleep(off_time)


class TemperatureProbe(object):

    def __init__(self):
        # Tell the temperature probe which ports its connected to (24, 23, and 18)
        self._sensor = MAX31855.MAX31855(24, 23, 18)
        log.debug("Connected to temperature probe.")

    @property
    def current_temperature(self):
        return self._sensor.readTempC()


class TemperatureController(object):
    def __init__(self, probe=None, output=None, data_provider=None):
        self._probe = probe
        self._output = output
        self._data_provider = data_provider
        self._pid = PID()
        self._program = TemperatureProgram()
        self._history_key = None
        self._start_time = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure that we've turned off the heater once the program finishes for any reason
        log.info("\n\nEnding run. Shutting off heater.")
        self._data_provider.deactivate()
        self._output.disable()
        log.info("Shutdown complete.\n\n")

    @property
    def start_time(self):
        if self._start_time is None:
            self._start_time = datetime.utcnow()
        return self._start_time

    def run(self):
        while True:
            self._listen()
            self._activate()
            self._run_program()

    def _listen(self):
        """
        Do nothing until someone instructs the temperature controller to start running.

        """
        while True:
            if self._data_provider.active:
                break
            else:
                log.debug("Temperature controller inactive.")
                time.sleep(2)

    def _activate(self):
        # get the program currently in Redis
        if not self._data_provider.manual:
            self._program.load_json(self._data_provider.program)
        # save the current timestamp so we can label data for the current run
        self._history_key = self._get_history_key()
        self._temp_log = logging.getLogger()
        handler = handlers.RotatingFileHandler("/var/log/temperatures/%s" % self._history_key)
        handler.setFormatter(logging.Formatter('%(asctime)s\t%(message)s'))
        self._temp_log.addHandler(handler)
        self._temp_log.setLevel(logging.INFO)
        if not self._data_provider.manual:
            self._program.start()

    def _run_program(self):
        # Activate the motor driver chip, but ensure the heater won't get hot until we want it to
        self._output.enable()
        self._output.set_pwm(0.0)
        while True:
            if not self._data_provider.active:
                # Turn off the heater and return to listening mode
                log.debug("The program has been disabled.")
                self._output.disable()
                break
            else:
                # We're still running the program. Update the PID and adjust the duty cycle accordingly
                temperature = self._update_temperature()
                self._temp_log.info(temperature)
                if self._data_provider.manual:
                    desired_temperature = float(self._data_provider.current_setting)
                else:
                    desired_temperature = self._program.get_desired_temperature()
                if desired_temperature is False:
                    self._data_provider.update_setting("Off!")
                    # the program is over
                    break
                else:
                    self._data_provider.update_setting("%.2f" % desired_temperature)
                log.debug("Desired temp: %s" % desired_temperature)
                self._pid.update_set_point(desired_temperature)
                new_duty_cycle = self._pid.update(temperature)
                # We add a slowdown factor here just as a hack to prevent the thing from heating too fast
                # Long term we should add back the derivative action
                SLOWDOWN_FACTOR = 0.2
                self._output.set_pwm(new_duty_cycle * SLOWDOWN_FACTOR)

    def _update_temperature(self):
        try:
            temperature = float(self._probe.current_temperature)
        except ValueError:
            return 100.0  # lol! this is extremely bad, fix this jim or everything will fail
        log.debug("Current temp: %s" % temperature)
        self._data_provider.update_temperature(temperature)
        try:
            self._data_provider.minutes_left = self._program.minutes_left
        except TypeError:
            self._data_provider.minutes_left = "n/a"
        return temperature

    def _get_history_key(self):
        history_key = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
        log.debug("History key: %s" % history_key)
        return history_key


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

    @property
    def minutes_left(self):
        seconds_left = max(self._total_duration - time.time() + self._start, 0)
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
        assert duration >= 60
        assert duration % 15 == 0
        total_diff = start_temperature - end_temperature
        setting_count = int(max(1, duration / 15))
        step_diff = total_diff / setting_count
        temperature = start_temperature
        for _ in xrange(setting_count):
            temperature -= step_diff
            setting = TemperatureSetting(float(temperature), 15)
            self._total_duration += 15
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

    def start(self):
        assert self._start is None
        self._start = time.time()

    def get_desired_temperature(self):
        elapsed = time.time() - self._start
        for setting in self._settings:
            elapsed -= setting.duration
            if elapsed < 0:
                return float(setting.temperature)
        # The program program is over or holding at a specified temperature.
        return float(self._hold_temp) if self._hold_temp else False


class PID:
    ROOM_TEMP = 20.0

    def __init__(self, kp=5.0, ki=2.0):
        self._kp = kp
        self._ki = ki
        self._previous_errors = []
        self._accumulated_error = 0.0
        self._accumulated_error_max = 20
        self._accumulated_error_min = -20
        self._set_point = 25.0

    def update(self, current_temperature):
        error = self.set_point - current_temperature
        log.debug("Error: %s" % error)
        # self._update_previous_errors(current_temperature, error)
        self._update_accumulated_error(error)
        p = self._kp * error
        log.debug("Proportional: %s" % p)
        i = self._accumulated_error * self._ki
        log.debug("Integral: %s" % i)
        total = 100 * int(p + i) / (self.set_point - PID.ROOM_TEMP + 5.0)
        log.debug("PI total: %s" % total)
        duty_cycle = max(0, min(100, total))
        log.debug("Duty cycle: %s" % duty_cycle)
        log.info("Temp: %s (error: %s)" % (current_temperature, -error))
        return duty_cycle

    def _update_accumulated_error(self, error):
        # Add the current error to the accumulated error
        self._accumulated_error += error
        # Ensure the value is within the allowed limits
        self._accumulated_error = min(self._accumulated_error, self._accumulated_error_max)
        self._accumulated_error = max(self._accumulated_error, self._accumulated_error_min)
        # log.debug("Accumulated error: %s" % self._accumulated_error)

    @property
    def set_point(self):
        return self._set_point

    def update_set_point(self, temperature):
        assert isinstance(temperature, float)
        log.debug("Setting set point to %s" % temperature)
        room_temp_diff = temperature - PID.ROOM_TEMP + 5.0
        self._accumulated_error_max = room_temp_diff / 2.0
        self._accumulated_error_min = -room_temp_diff / 2.0
        self._set_point = temperature
