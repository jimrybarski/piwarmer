"""
This is great and all, but you need to think hard about how you'll carry state around.
Also where errors occur and how you'll handle partial compliance.

"""
from datetime import datetime
import logging
import math
from rpid.api import APIData
from rpid.pid import PID, Driver
from rpid.thermometer import Thermometer
from rpid.program import TemperatureProgram
from rpid.heater import Heater
import time

log = logging.getLogger(__name__)



def listen():
    api_data = APIData()
    while True:
        if api_data.active:
            break
        else:
            log.debug("Temperature controller inactive.")
            time.sleep(2)

def activate():
    driver = Driver("small aluminum block", 5.0, 1.0, 0.0, 10.0, -10.0)
    thermometer = Thermometer()
    pid = PID(driver)
    start_time = datetime.utcnow()


def run_program():
    program = TemperatureProgram()


def run_manual():
    while True:
        pass


while True:
    try:
        heater = Heater()
        api_data = APIData()

        listen()
        mode = activate()
        if mode == "program":
            run_program()
        else:
            run_manual()
    except:
        log.exception("Unhandled exception!")
    finally:
        log.info("\n\nEnding run. Shutting off heater.")
        api_data.deactivate()
        heater.disable()
        log.info("Shutdown complete.\n\n")


    def _activate(self):
        # get the program currently in Redis
        if not self._data_provider.manual:
            self._program.load_json(self._data_provider.program)
        # save the current timestamp so we can label data for the current run
        self._history_key = self._get_history_key()
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
        current_temp = self._probe.current_temperature
        if math.isnan(current_temp):
            current_temp = self._data_provider.current_temp or 20.0
        temperature = float(current_temp)

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
