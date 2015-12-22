import collections
import numpy as np


class Driver(object):
    def __init__(self, name, kp, ki, kd, error_max, error_min):
        self.name = name
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_max = error_max
        self.error_min = error_min


class PID(object):
    """
    Calculates what duty cycle would be best to achieve a certain temperature, while attempting to prevent overshooting (and undershooting).

    """
    ROOM_TEMP = 20.0

    def __init__(self, driver, memory=6):
        self._kp = driver.kp
        self._ki = driver.ki
        self._kd = driver.kd
        self._accumulated_error_max = driver.error_max
        self._accumulated_error_min = driver.error_min
        # generate some things needed to calculate the derivative
        x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
        self._ticks = np.vstack([x, np.ones(len(x))]).T
        self._past_errors = collections.deque([0.0, 0.0, 0.0, 0.0, 0.0], maxlen=memory)

    def update(self, cycle_data):
        assert cycle_data.desired_temperature is not None
        assert cycle_data.current_temperature is not None
        assert cycle_data.accumulated_error is not None

        error = cycle_data.desired_temperature - cycle_data.current_temperature
        self._past_errors.append(error)
        new_accumulated_error = self._calculate_accumulated_error(error, cycle_data.accumulated_error)
        p = self._kp * error
        i = new_accumulated_error * self._ki
        d = self._kd * np.linalg.lstsq(self._ticks, np.array(self._past_errors))[0][0]
        # scale the result by the temperature to give it some approximation of the neighborhood it should be in
        # I don't think this is mathematically sound and might just work purely by coincidence
        total = 100 * int(p + i + d) / abs(cycle_data.desired_temperature)
        duty_cycle = max(0, min(100, total))
        return duty_cycle, new_accumulated_error

    def _calculate_accumulated_error(self, error, accumulated_error):
        # Add the current error to the accumulated error
        new_accumulated_error = accumulated_error + error
        # Ensure the value is within the allowed limits
        new_accumulated_error = min(new_accumulated_error, self._accumulated_error_max)
        new_accumulated_error = max(new_accumulated_error, self._accumulated_error_min)
        return new_accumulated_error
