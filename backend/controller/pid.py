class Driver(object):
    def __init__(self, name, kp, ki, kd, error_max, error_min):
        self._name = name
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._error_max = error_max
        self._error_min = error_min

    @property
    def kp(self):
        return self._kp

    @property
    def ki(self):
        return self._ki

    @property
    def kd(self):
        return self._kd

    @property
    def error_max(self):
        return self._error_max

    @property
    def error_min(self):
        return self._error_min


class PID:
    ROOM_TEMP = 20.0

    def __init__(self, driver):
        self._kp = driver.kp
        self._ki = driver.ki
        self._accumulated_error_max = driver.error_max
        self._accumulated_error_min = driver.error_min

    def update(self, data):
        assert data.desired_temperature is not None
        assert data.current_temperature is not None
        assert data.accumulated_error is not None

        error = data.desired_temperature - data.current_temperature
        new_accumulated_error = self._calculate_accumulated_error(error, data.accumulated_error)
        p = self._kp * error
        i = new_accumulated_error * self._ki
        # scale the result by the temperature to give it some approximation of the neighborhood it should be in
        # I don't think this is mathematically sound and might just work purely by coincidence
        total = 100 * int(p + i) / abs(data.desired_temperature)
        duty_cycle = max(0, min(100, total))
        return duty_cycle, new_accumulated_error

    def _calculate_accumulated_error(self, error, accumulated_error):
        # Add the current error to the accumulated error
        new_accumulated_error = accumulated_error + error
        # Ensure the value is within the allowed limits
        new_accumulated_error = min(new_accumulated_error, self._accumulated_error_max)
        new_accumulated_error = max(new_accumulated_error, self._accumulated_error_min)
        return new_accumulated_error
