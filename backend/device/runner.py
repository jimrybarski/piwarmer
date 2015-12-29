from abc import abstractmethod
import cycle
from datetime import datetime
import logging
import pid
import program
import time


log = logging.getLogger(__name__)


class BaseRunner(object):
    """
    These methods are implemented here in this base class because we foresee the possibility that people might
    want to have some kind of manual control mode, where they can adjust the temperature on the fly without a
    program. That has not yet been written though.

    """
    def __init__(self, api_interface, thermometer, heater):
        self._api_interface = api_interface
        self._thermometer = thermometer
        self._heater = heater

    def run(self):
        """
        The main loop basically just waits for a program to show up in Redis, and runs it until it's told to stop,
        then it resets all values and starts all over again.

        """
        while True:
            self._boot()
            self._listen()
            self._prerun()
            self._run()

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug("Exiting program runner.")
        if exc_type:
            log.exception("Abnormal termination!")
        self._shutdown()

    def _shutdown(self):
        """
        Physically turns off the heater and clears the program from memory.

        """
        log.debug("Shutting down heater...")
        try:
            self._heater.disable()
        except:
            log.exception("DANGER! HEATER DID NOT SHUT DOWN")
        else:
            log.debug("Heater shutdown successful.")
        log.debug("Clearing API data.")
        try:
            self._api_interface.clear()
        except:
            log.exception("Failed to clear API data!")
        else:
            log.debug("API data cleared.")

    def __enter__(self):
        return self

    def _boot(self):
        """
        Unsets the current program. We require that this runs before every loop to prevent accidentally starting a program whose parameters were somehow left in Redis.
        This was a problem even after the Raspberry Pi was physically disconnected from the power supply.

        """
        log.info("Booting! About to clear API data")
        self._api_interface.clear()

    def _listen(self):
        """
        Wait until the "active" key is on in Redis before starting a program.

        """
        while True:
            if self._api_interface.active:
                log.info("The system has been activated")
                break
            else:
                try:
                    # update the current temperature in Redis so that we can see how hot the heater is, even if we're not running a program
                    self._api_interface.current_temp = self._thermometer.current_temperature
                except:
                    # absolutely do not allow this loop to terminate. Though if it did, supervisord would restart the process, but that's annoying and
                    # results in some downtime
                    log.exception("Something went wrong in the _listen() loop!")
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
    Runs a pre-defined program, and ensures that shutdown.

    """
    def __init__(self, current_state, thermometer, heater, log_dir='/var/log/piwarmer'):
        super(ProgramRunner, self).__init__(current_state, thermometer, heater)
        self._accumulated_error = None
        self._log_dir = log_dir.rstrip("/")
        self._pid = None
        self._program = None
        self._start_time = None
        self._temperature_log = None

    def _prerun(self):
        """
        Set up the PID for temperature control.

        """
        driver = self._api_interface.driver
        driver = pid.Driver(driver['name'], driver['kp'], driver['ki'], driver['kd'],
                            driver['max_accumulated_error'], driver['min_accumulated_error'])
        self._pid = pid.PID(driver)
        self._accumulated_error = 0.0
        self._start_time = datetime.utcnow()
        log.info("Program start time: %s" % self._start_time)
        self._temperature_log = self._get_temperature_log()
        self._program = program.TemperatureProgram(self._api_interface.program)
        self._heater.enable()

    def _get_temperature_log(self):
        """
        Creates a machine-readable log of the temperature, the target temperature, and the duty cycle at 1-second intervals.

        """
        # Set up another logger for temperature logs
        temperature_log = logging.getLogger("temperatures")
        handler = logging.FileHandler('%s/temperature-%s.log' % (self._log_dir, self._start_time.strftime("%Y-%m-%d-%H-%M-%S")))
        formatter = logging.Formatter('%(asctime)s\t%(message)s')
        handler.setFormatter(formatter)
        temperature_log.addHandler(handler)
        temperature_log.setLevel(logging.INFO)
        return temperature_log

    def _run(self):
        """
        The main program loop. We figure out what step we're on, whether the heater needs to be turned on, and whether it's time to shutdown.

        """
        assert self._api_interface is not None
        assert self._start_time is not None
        assert self._thermometer is not None
        assert self._accumulated_error is not None

        while self._api_interface.active:
            # make some safe assignments that should never fail
            current_cycle = cycle.CurrentCycle()
            current_cycle.accumulated_error = self._accumulated_error
            current_cycle.current_time = datetime.utcnow()
            current_cycle.start_time = self._start_time
            current_cycle.program = self._program
            current_cycle.skip_time = self._api_interface.skip_time

            if current_cycle.current_step is None:
                # the program is over and we're not using a Hold setting
                log.info("There are no more steps to run in the current program. Shutting down...")
                break

            # I/O - read the temperature. This operation is blocking!
            current_cycle.current_temperature = self._thermometer.current_temperature

            # make calculations based on I/O having worked
            current_cycle.duty_cycle, self._accumulated_error = self._pid.update(current_cycle)

            # save the temperature information to a machine-readable log file
            self._temperature_log.info("%s\t%s\t%s" % (current_cycle.current_temperature,
                                                       current_cycle.target_temperature,
                                                       current_cycle.duty_cycle))
            # physically activate the heater, if necessary
            self._heater.heat(current_cycle.duty_cycle)

            # update the API data so the frontend can know what's happening
            self._api_interface.current_temp = current_cycle.current_temperature
            self._api_interface.target_temp = current_cycle.target_temperature
            self._api_interface.current_step = current_cycle.current_step
            self._api_interface.program_time_remaining = current_cycle.seconds_left
            self._api_interface.step_time_remaining = current_cycle.step_time_remaining

        self._shutdown()
