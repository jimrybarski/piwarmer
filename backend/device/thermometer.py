import logging
import math

log = logging.getLogger(__name__)


class Thermometer(object):
    """
    Gets temperature values from a temperature probe and reports them.

    """
    def __init__(self, sensor):
        self._sensor = sensor
        log.debug("Successfully connected to temperature probe.")

    @property
    def current_temperature(self):
        """
        The chip that we use, the MAX31855, doesn't always return a numeric value - sometimes it returns NaN for
        unknown reasons. To get around this, we just keep reading until we get a number back. This hasn't been a problem
        since the periods where it returns NaN usually only last for a few milliseconds and are relatively sparse.

        Note that this method is blocking! If you unplug the probe, the entire script will halt until you plug it back in!

        :rtype:     float

        """
        temperature = float('NaN')
        while math.isnan(temperature):
            temperature = float(self._sensor.readTempC())
        return temperature
