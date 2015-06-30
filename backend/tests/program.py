import unittest
from rpid.program import TemperatureSetting, TemperatureProgram, get_desired_temperature
from rpid.data import RoundData
from datetime import datetime


class LinearGradientTests(unittest.TestCase):
    def test_get_temp1(self):
        lg = TemperatureSetting(0, 100, 10)
        self.assertEqual(lg.get_temperature(0), 0.0)
        self.assertEqual(lg.get_temperature(1), 10.0)
        self.assertEqual(lg.get_temperature(2), 20.0)
        self.assertEqual(lg.get_temperature(3), 30.0)
        self.assertEqual(lg.get_temperature(4), 40.0)
        self.assertEqual(lg.get_temperature(5), 50.0)

    def test_get_temp2(self):
        lg = TemperatureSetting(100, 0, 10)
        self.assertEqual(lg.get_temperature(0), 100.0)
        self.assertEqual(lg.get_temperature(1), 90.0)
        self.assertEqual(lg.get_temperature(2), 80.0)
        self.assertEqual(lg.get_temperature(3), 70.0)
        self.assertEqual(lg.get_temperature(4), 60.0)
        self.assertEqual(lg.get_temperature(5), 50.0)

    def test_get_temp3(self):
        lg = TemperatureSetting(1, 9, 10)
        self.assertEqual(lg.get_temperature(0), 1.0)
        self.assertEqual(lg.get_temperature(1), 1.8)
        self.assertEqual(lg.get_temperature(2), 2.6)
        self.assertEqual(lg.get_temperature(3), 3.4)
        self.assertEqual(lg.get_temperature(4), 4.2)
        self.assertEqual(lg.get_temperature(5), 5.0)


class TemperatureProgramTests(unittest.TestCase):
    def setUp(self):
        self.program = TemperatureProgram("""{
              "1": {"mode": "set", "temperature": 80.0, "duration": 300},
              "2": {"mode": "linear", "start_temperature": 80.0, "end_temperature": 30.0, "duration": 3600},
              "3": {"mode": "hold", "temperature": 37.0}}""")
        self.rd = RoundData()
        self.rd.program = self.program

    def test_duration(self):
        self.assertEqual(self.program.total_duration, 3900)

    def test_get_desired_temperature(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 12, 12)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        temp = get_desired_temperature(self.rd)
        self.assertEqual(temp, 80.0)

    def test_get_linear_gradient_temperature(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 45, 12)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        temp = get_desired_temperature(self.rd)
        self.assertEqual(temp, 55.0)