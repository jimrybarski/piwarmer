import unittest
from backend.device.thermometer import Thermometer
from backend.device.dummy import MockMAX31855
import math


class ThermometerTests(unittest.TestCase):
    def setUp(self):
        self.thermometer = Thermometer(MockMAX31855())

    def test_read_c(self):
        for i in range(10000):
            temperature = self.thermometer.current_temperature
            self.assertFalse(math.isnan(temperature))
