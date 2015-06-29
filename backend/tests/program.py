import unittest
from rpid.program import LinearGradient


class LinearGradientTests(unittest.TestCase):
    def test_get_temp1(self):
        lg = LinearGradient(0, 100, 10)
        self.assertEqual(lg.get_temperature(0), 0.0)
        self.assertEqual(lg.get_temperature(1), 10.0)
        self.assertEqual(lg.get_temperature(2), 20.0)
        self.assertEqual(lg.get_temperature(3), 30.0)
        self.assertEqual(lg.get_temperature(4), 40.0)
        self.assertEqual(lg.get_temperature(5), 50.0)

    def test_get_temp2(self):
        lg = LinearGradient(100, 0, 10)
        self.assertEqual(lg.get_temperature(0), 100.0)
        self.assertEqual(lg.get_temperature(1), 90.0)
        self.assertEqual(lg.get_temperature(2), 80.0)
        self.assertEqual(lg.get_temperature(3), 70.0)
        self.assertEqual(lg.get_temperature(4), 60.0)
        self.assertEqual(lg.get_temperature(5), 50.0)