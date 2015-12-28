import unittest
from backend.device.heater import Heater
from backend.device.dummy import MockGPIO


class HeaterTests(unittest.TestCase):
    def setUp(self):
        self.heater = Heater(MockGPIO)

    def test_calculate_pwm_0(self):
        on_time, off_time = self.heater._calculate_pwm(0)
        self.assertEqual(on_time, 0.0)
        self.assertEqual(off_time, 1.0)

    def test_calculate_pwm_20(self):
        on_time, off_time = self.heater._calculate_pwm(20)
        self.assertEqual(on_time, 0.2)
        self.assertEqual(off_time, 0.8)

    def test_calculate_pwm_50(self):
        on_time, off_time = self.heater._calculate_pwm(50)
        self.assertEqual(on_time, 0.5)
        self.assertEqual(off_time, 0.5)
        self.assertEqual(on_time, off_time)

    def test_calculate_pwm_100(self):
        on_time, off_time = self.heater._calculate_pwm(100)
        self.assertEqual(on_time, 1.0)
        self.assertEqual(off_time, 0.0)
