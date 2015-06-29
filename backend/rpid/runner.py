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

            # make some safe assignments that should never fail
            round_data = data.RoundData()
            round_data.accumulated_error = self._accumulated_error
            round_data.current_time = datetime.utcnow()
            round_data.start_time = self._start_time
            round_data.program = self._program

            # derive some data from the things that were just assigned
            round_data.desired_temperature = program.get_desired_temperature(round_data)
            round_data.seconds_left = program.calculate_seconds_left(round_data)

            # I/O - read the temperature
            round_data.current_temperature = self._thermometer.current_temperature

            if not round_data.can_update_pid:
                # something went wrong - maybe the thermometer returned NaN as it does sometimes,
                # maybe something got unplugged. We'll just try again until explicitly told to stop
                continue

            # make calculations based on I/O having worked
            round_data.duty_cycle, self._accumulated_error = self._pid.update(round_data)
            self._heater.heat(round_data.duty_cycle)
