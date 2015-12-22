import collections
import numpy as np


class Driver(object):
    """
    Just a container for PID values.

    """
    def __init__(self, name, kp, ki, kd, error_max, error_min):
        self.name = name
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.error_max = error_max
        self.error_min = error_min


class PID(object):
    """
    Calculates what duty cycle would be best to achieve a certain temperature, while attempting to minimize error and prevent oscillation around the target temperature.

    """
    def __init__(self, driver, memory=4):
        """

        :param driver:    a Driver object that provides all the PID parameters
        :param memory:    the number of previous cycles to use in the calculation of the error derivative

        """
        memory = int(memory)
        assert memory > 0
        self._kp = driver.kp
        self._ki = driver.ki
        self._kd = driver.kd
        self._accumulated_error_max = driver.error_max
        self._accumulated_error_min = driver.error_min
        # generate some things needed to calculate the derivative
        ticks = np.array([float(i) for i in range(memory)])
        self._ticks = np.vstack([ticks, np.ones(memory)]).T
        # seed the past errors with zeros. this will diminish the effect of the derivative for the
        # first few (i.e. len(memory)) seconds, but after that it will be correct. It is therefore best
        # to use a small value for memory, probably less than 10
        self._past_errors = collections.deque([0.0 for _ in range(memory)], maxlen=memory)

    def update(self, cycle_data):
        """
        Give the PID new data and get back what the duty cycle should be.

        """
        assert cycle_data.desired_temperature is not None
        assert cycle_data.current_temperature is not None
        assert cycle_data.accumulated_error is not None

        error = cycle_data.desired_temperature - cycle_data.current_temperature
        self._past_errors.append(error)
        error_integral = self._calculate_integral(error, cycle_data.accumulated_error)
        p = self._kp * error
        i = self._ki * error_integral
        d = self._calculate_derivative(self._kd, self._past_errors)
        # duty cycle is bounded from 0% to 100%
        duty_cycle = max(0, min(100, int(p + i + d)))
        return duty_cycle, error_integral

    def _calculate_integral(self, error, accumulated_error):
        """
        Calculates the value used by the integral part of the equation and ensures it's within the given bounds.

        """
        # Add the current error to the accumulated error
        new_accumulated_error = accumulated_error + error
        # Ensure the value is within the allowed limits
        new_accumulated_error = min(new_accumulated_error, self._accumulated_error_max)
        new_accumulated_error = max(new_accumulated_error, self._accumulated_error_min)
        return new_accumulated_error

    def _calculate_derivative(self, kd, past_errors):
        """
        Computes the derivative of the recent differences between the desired temperature and the actual temperature.

        """
        return kd * np.linalg.lstsq(self._ticks, np.array(past_errors))[0][0]
