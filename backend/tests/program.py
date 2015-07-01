import unittest
from rpid.program import TemperatureSetting, TemperatureProgram, get_desired_temperature, get_next_n_settings
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

    def test_get_hold_temperature(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 12, 12)
        self.rd.start_time = datetime(2015, 12, 12, 12, 10, 12)  # three years later
        temp = get_desired_temperature(self.rd)
        self.assertEqual(temp, 37.0)


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

    def test_get_linear_gradient_temperature2(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 21, 12)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        temp = get_desired_temperature(self.rd)
        self.assertEqual(temp, 75.0)

    def test_get_linear_gradient_temperature3(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 15, 12)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        temp = get_desired_temperature(self.rd)
        self.assertEqual(temp, 80.0)

    def test_get_linear_gradient_temperature4(self):
        self.rd.current_time = datetime(2012, 12, 12, 12, 15, 42)
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        temp = get_desired_temperature(self.rd)
        self.assertAlmostEqual(temp, 79.583333333)


class TemperatureDisplayTests(unittest.TestCase):
    def setUp(self):
        self.program = TemperatureProgram("""{
              "1": {"mode": "set", "temperature": 80.0, "duration": 120},
              "2": {"mode": "linear", "start_temperature": 80.0, "end_temperature": 30.0, "duration": 180},
              "3": {"mode": "linear", "start_temperature": 80.0, "end_temperature": 30.0, "duration": 240},
              "4": {"mode": "set", "temperature": 80.0, "duration": 60},
              "5": {"mode": "set", "temperature": 80.0, "duration": 120},
              "6": {"mode": "set", "temperature": 80.0, "duration": 180},
              "7": {"mode": "set", "temperature": 80.0, "duration": 240},
              "8": {"mode": "hold", "temperature": 37.0}}""")

    def test_get_n_next_settings(self):
        self.rd = RoundData()
        self.rd.program = self.program
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        self.rd.current_time = datetime(2012, 12, 12, 12, 11, 57)
        settings = get_next_n_settings(5, self.rd)
        times = [s[1] for s in settings]
        self.assertListEqual(times, ["Now Running", "00:00:15", "00:03:15", "00:07:15", "00:08:15"])
        messages = [s[0].message for s in settings]
        self.assertListEqual(messages, ["80.0&deg;C for 00:02:00",
                                        "From 80.0&deg;C to 30.0&deg;C over 00:03:00",
                                        "From 80.0&deg;C to 30.0&deg;C over 00:04:00",
                                        "80.0&deg;C for 00:01:00",
                                        "80.0&deg;C for 00:02:00"])

    def test_get_n_next_settings_fewer_available_than_asked_for(self):
        self.rd = RoundData()
        self.rd.program = self.program
        self.rd.start_time = datetime(2012, 12, 12, 12, 10, 12)
        self.rd.current_time = datetime(2012, 12, 12, 12, 22, 27)
        settings = get_next_n_settings(5, self.rd)
        times = [s[1] for s in settings]
        self.assertListEqual(times, ["Now Running", "00:02:45", "00:06:45"])
        messages = [s[0].message for s in settings]
        self.assertListEqual(messages, ["80.0&deg;C for 00:03:00",
                                        "80.0&deg;C for 00:04:00",
                                        "Hold at 37.0&deg;C"])
