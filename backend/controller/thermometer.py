from dummy import FakeMAX31855
import logging
import math

try:
    import Adafruit_MAX31855.MAX31855 as MAX31855
except ImportError:
    MAX31855 = FakeMAX31855

# Because they have an annoying and useless message
maxlog = logging.getLogger('Adafruit_MAX31855.MAX31855')
maxlog.disabled = True

log = logging.getLogger(__name__)


class Thermometer(object):

    def __init__(self):
        # Tell the temperature probe which ports its connected to (24, 23, and 18)
        self._sensor = MAX31855.MAX31855(24, 23, 18)
        log.debug("Successfully connected to temperature probe.")

    @property
    def current_temperature(self):
        temperature = float(self._sensor.readTempC())
        return None if math.isnan(temperature) else temperature
