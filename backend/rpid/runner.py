"""
This is great and all, but you need to think hard about how you'll carry state around.
Also where errors occur and how you'll handle partial compliance.

"""
from abc import abstractmethod
from datetime import datetime
import logging
from rpid import program, thermometer, heater, pid, data, api
import time

log = logging.getLogger(__name__)


class BaseRunner(object):
    def __init__(self):
        self._api_data = api.APIData()
        self._thermometer = thermometer.Thermometer()

    def run(self):
        while True:
            self._boot()
            self._listen()
            self._prerun()
            self._run()

    def __enter__(self):
        return self

    def _boot(self):
        self._api_data.clear()

    def _listen(self):
        while True:
            if self._api_data.active:
                break
            else:
                try:
                    # try to display the current temperature if at all possible
                    self._api_data.update_temperature(self._thermometer.current_temperature)
                except:
                    pass
                time.sleep(1)

    @abstractmethod
    def _prerun(self):
        """
        Things that need to be done before the run starts.

        """
        raise NotImplemented

    @abstractmethod
    def _run(self):
        """
        What to do when the heater should potentially be on.

        """
        raise NotImplemented


class ProgramRunner(BaseRunner):
    """
    Runs a pre-defined program.

    """
    def __init__(self):
        super(ProgramRunner, self).__init__()
        self._heater = heater.Heater()
        self._start_time = None
        self._program = None
        self._accumulated_error = None
        self._pid = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._shutdown()

    def _shutdown(self):
        try:
            self._heater.disable()
        except:
            pass
        try:
            self._api_data.clear()
        except:
            pass

    def _prerun(self):
        # in the near future, the driver will be chosen by the user
        driver = pid.Driver("small aluminum block", 5.0, 1.0, 0.0, 10.0, -10.0)
        self._pid = pid.PID(driver)
        assert self._start_time is None
        assert self._program is None
        self._accumulated_error = 0.0
        self._start_time = datetime.utcnow()
        self._program = program.TemperatureProgram(self._api_data.program)

    def _run(self):
        """
        Are we still running?
        What is the current temperature?
        What should the temperature be?
        Run the heater if needed.
        Update the API information.

        """
        while True:
            assert self._start_time is not None
            assert self._api_data is not None
            assert self._thermometer is not None
            assert self._accumulated_error is not None

            if not self._api_data.active:
                self._shutdown()
                break

            # get derived data and data from the API - essentially the safe actions that should never fail
            round_data = data.RoundData()
            round_data.start_time = self._start_time
            round_data.current_time = datetime.utcnow()
            round_data.accumulated_error = self._accumulated_error
            round_data.program = self._program
            round_data.desired_temperature = program.get_desired_temperature(round_data)
            round_data.seconds_left = program.calculate_seconds_left(round_data)

            # I/O - read the temperature
            round_data.current_temperature = self._thermometer.current_temperature

            if not round_data.can_update_pid:
                continue

            # make calculations based on I/O having worked
            round_data.duty_cycle, self._accumulated_error = self._pid.update(round_data)
            self._heater.heat(round_data.duty_cycle)

# def run_program():
#     program = TemperatureProgram()
#
#
# def run_manual():
#     while True:
#         pass

#
# while True:
#     try:
#         heater = Heater()
#         api_data = APIData()
#
#         listen()
#         mode = activate()
#             run_program()
#         else:
#             run_manual()
#     except:
#         log.exception("Unhandled exception!")
#     finally:
#         log.info("\n\nEnding run. Shutting off heater.")
#         api_data.deactivate()
#         heater.disable()
#         log.info("Shutdown complete.\n\n")
#
#
#     def _activate(self):
#         # get the program currently in Redis
#         if not self._data_provider.manual:
#             self._program.load_json(self._data_provider.program)
#         # save the current timestamp so we can label data for the current run
#         self._history_key = self._get_history_key()
#         if not self._data_provider.manual:
#             self._program.start()
#
#     def _run_program(self):
#         # Activate the motor driver chip, but ensure the heater won't get hot until we want it to
#         self._output.enable()
#         self._output.set_pwm(0.0)
#         while True:
#             if not self._data_provider.active:
#                 # Turn off the heater and return to listening mode
#                 log.debug("The program has been disabled.")
#                 self._output.disable()
#                 break
#             else:
#                 # We're still running the program. Update the PID and adjust the duty cycle accordingly
#                 temperature = self._update_temperature()
#                 self._temp_log.info(temperature)
#                 if self._data_provider.manual:
#                     desired_temperature = float(self._data_provider.current_setting)
#                 else:
#                     desired_temperature = self._program.get_desired_temperature()
#                 if desired_temperature is False:
#                     self._data_provider.update_setting("Off!")
#                     # the program is over
#                     break
#                 else:
#                     self._data_provider.update_setting("%.2f" % desired_temperature)
#                 log.debug("Desired temp: %s" % desired_temperature)
#                 self._pid.update_set_point(desired_temperature)
#                 new_duty_cycle = self._pid.update(temperature)
#                 # We add a slowdown factor here just as a hack to prevent the thing from heating too fast
#                 # Long term we should add back the derivative action
#                 SLOWDOWN_FACTOR = 0.2
#                 self._output.set_pwm(new_duty_cycle * SLOWDOWN_FACTOR)
#
#     def _update_temperature(self):
#         current_temp = self._probe.current_temperature
#         if math.isnan(current_temp):
#             current_temp = self._data_provider.current_temp or 20.0
#         temperature = float(current_temp)
#
#         log.debug("Current temp: %s" % temperature)
#         self._data_provider.update_temperature(temperature)
#         try:
#             self._data_provider.minutes_left = self._program.minutes_left
#         except TypeError:
#             self._data_provider.minutes_left = "n/a"
#         return temperature
#
#     def _get_history_key(self):
#         history_key = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
#         log.debug("History key: %s" % history_key)
#         return history_key
