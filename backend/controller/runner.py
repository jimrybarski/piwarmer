from abc import abstractmethod
from datetime import datetime
import logging
from controller import program, thermometer, heater, pid, data
from interface import APIData
import time

log = logging.getLogger(__name__)


class BaseRunner(object):
    """
    These methods are implemented here in this base class because we foresee the possibility that people might
    want to have some kind of manual control mode, where they can adjust the temperature on the fly without a
    program. That has not yet been written though.

    """
    def __init__(self):
        self._api_data = APIData()
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
        log.info("Booting! About to clear API data")
        self._api_data.clear()

    def _listen(self):
        while True:
            if self._api_data.active:
                log.info("We need to run a program!")
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
        self._temperature_log = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug("Exiting program runner.")
        if exc_type:
            log.exception("Abnormal termination!")
        self._shutdown()

    def _shutdown(self):
        log.debug("Shutting down heater.")
        try:
            self._heater.disable()
        except:
            log.critical("DANGER! HEATER DID NOT SHUT DOWN")
        else:
            log.debug("Heater shutdown successful.")
        log.debug("Clearing API data.")
        try:
            self._api_data.clear()
        except:
            log.exception("Failed to clear API data!")
        else:
            log.debug("API data cleared.")

    def _prerun(self):
        driver = self._api_data.driver
        driver = pid.Driver(driver['name'], driver['kp'], driver['ki'], driver['kd'],
                            driver['max_accumulated_error'], driver['min_accumulated_error'])
        self._pid = pid.PID(driver)
        self._accumulated_error = 0.0
        self._start_time = datetime.utcnow()
        log.info("Start time: %s" % self._start_time)

        # Set up another logger for temperature logs
        self._temperature_log = logging.getLogger("temperatures")
        handler = logging.FileHandler('/var/log/piwarmer/temperature-%s.log' % self._start_time.strftime("%Y-%m-%d"))
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self._temperature_log.addHandler(handler)
        self._temperature_log.setLevel(logging.INFO)
        self._program = program.TemperatureProgram(self._api_data.program)
        self._heater.enable()

    def _run(self):
        """
        1. Are we still running?
        2. What is the current temperature?
        3. What should the temperature be?
        4. Physically activate the heater if needed.
        5. Update the API information.

        """
        while True:
            assert self._start_time is not None
            assert self._api_data is not None
            assert self._thermometer is not None
            assert self._accumulated_error is not None

            if not self._api_data.active:
                log.info("The program has ended or been stopped")
                self._shutdown()
                break

            # make some safe assignments that should never fail
            round_data = data.RoundData()
            round_data.accumulated_error = self._accumulated_error
            round_data.current_time = datetime.utcnow()
            round_data.start_time = self._start_time
            round_data.program = self._program
            # derive some data from the things that were just assigned
            round_data.desired_temperature = program.get_desired_temperature(round_data)
            log.info("desired temp\t%s" % round_data.desired_temperature)
            round_data.seconds_left = program.calculate_seconds_left(round_data)
            round_data.next_steps, round_data.times_until = program.get_next_n_settings(5, round_data)

            # the program is over and we're not using a Hold setting
            if not round_data.next_steps:
                log.info("We're out of steps to run, so we should shut down now.")
                self._shutdown()
                break

            # I/O - read the temperature
            round_data.current_temperature = self._thermometer.current_temperature
            if not round_data.can_update_pid:
                # something went wrong - maybe the thermometer returned NaN as it does sometimes,
                # maybe something got unplugged. We'll just try again until explicitly told to stop
                log.warn("Can't update PID!")
                continue

            # make calculations based on I/O having worked
            round_data.duty_cycle, self._accumulated_error = self._pid.update(round_data)

            self._temperature_log.info("%s\t%s\t%s" % (round_data.current_temperature,
                                                       round_data.desired_temperature,
                                                       round_data.duty_cycle))
            # run the heating sequence, if necessary
            self._heater.heat(round_data.duty_cycle)

            # update the API data so the frontend can know what's happening
            self._api_data.time_left = program.convert_seconds_to_hhmmss(round_data.seconds_left)
            self._api_data.update_temperature(round_data.current_temperature)
            self._api_data.update_setting(round_data.desired_temperature)
            self._api_data.update_next_steps(round_data.next_steps, round_data.times_until)
