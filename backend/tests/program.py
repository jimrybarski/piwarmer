import unittest
from backend.device.cycle import CurrentCycle
from backend.device.program import TemperatureProgram, TemperatureSetting
from datetime import datetime


class LinearGradientTests(unittest.TestCase):
    def test_get_temp1(self):
        lg = TemperatureSetting(0, 0, 100, 10)
        self.assertEqual(lg.get_temperature(0), 0.0)
        self.assertEqual(lg.get_temperature(1), 10.0)
        self.assertEqual(lg.get_temperature(2), 20.0)
        self.assertEqual(lg.get_temperature(3), 30.0)
        self.assertEqual(lg.get_temperature(4), 40.0)
        self.assertEqual(lg.get_temperature(5), 50.0)

    def test_get_temp2(self):
        lg = TemperatureSetting(0, 100, 0, 10)
        self.assertEqual(lg.get_temperature(0), 100.0)
        self.assertEqual(lg.get_temperature(1), 90.0)
        self.assertEqual(lg.get_temperature(2), 80.0)
        self.assertEqual(lg.get_temperature(3), 70.0)
        self.assertEqual(lg.get_temperature(4), 60.0)
        self.assertEqual(lg.get_temperature(5), 50.0)

    def test_get_temp3(self):
        lg = TemperatureSetting(77, 1, 9, 10)
        self.assertEqual(lg.get_temperature(0), 1.0)
        self.assertEqual(lg.get_temperature(1), 1.8)
        self.assertEqual(lg.get_temperature(2), 2.6)
        self.assertEqual(lg.get_temperature(3), 3.4)
        self.assertEqual(lg.get_temperature(4), 4.2)
        self.assertEqual(lg.get_temperature(5), 5.0)


class TemperatureProgramTests(unittest.TestCase):
    def setUp(self):
        self.program = TemperatureProgram({
              "1": {"mode": "set", "temperature": 80.0, "duration": 300},
              "2": {"mode": "linear", "start_temperature": 80.0, "end_temperature": 30.0, "duration": 3600},
              "3": {"mode": "hold", "temperature": 37.0}})
        self.rd = CurrentCycle()
        self.rd.program = self.program

    def test_duration(self):
        self.assertEqual(self.program.total_duration, 3900)

    def test_get_hold_temperature(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 12, 12)
        self.rd.start_time = datetime(2015, 12, 12, 12, 10, 12)  # three years later
        self.assertEqual(self.rd.desired_temperature, 37.0)

    def test_get_desired_temperature(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 12, 12)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        self.assertEqual(self.rd.desired_temperature, 80.0)

    def test_get_linear_gradient_temperature(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 45, 12)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        self.assertEqual(self.rd.desired_temperature, 55.0)

    def test_get_linear_gradient_temperature2(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 21, 12)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        self.assertEqual(self.rd.desired_temperature, 75.0)

    def test_get_linear_gradient_temperature3(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 15, 12)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        self.assertEqual(self.rd.desired_temperature, 80.0)

    def test_get_linear_gradient_temperature4(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 15, 42)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        self.assertAlmostEqual(self.rd.desired_temperature, 79.583333333)
