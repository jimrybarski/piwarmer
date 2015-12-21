import logging
import math

log = logging.getLogger(__name__)


class Thermometer(object):
    """

    """
    def __init__(self, sensor):
        # Tell the temperature probe which ports it's connected to (24, 23, and 18)
        self._sensor = sensor
        log.debug("Successfully connected to temperature probe.")

    @property
    def current_temperature(self):
        temperature = None
        while temperature is None:
            temperature = float(self._sensor.readTempC())
            temperature = None if math.isnan(temperature) else temperature
        return temperature
