import unittest
from backend.device.pid import PID, Driver


class PIDTests(unittest.TestCase):
    def setUp(self):
        driver = Driver('test', 1.0, 1.0, 1.0, 10.0, -10.0)
        self.pid = PID(driver)

    def test_calculate_derivative_default_values(self):
        d = self.pid._calculate_derivative(1.0, self.pid._past_errors)
        self.assertEqual(d, 0.0)

    def test_calculate_derivative_some_values(self):
        d = self.pid._calculate_derivative(1.0, [2.0, 4.0, 6.0, 8.0, 10.0, 12.0])
        self.assertAlmostEqual(d, 2.0)

    def test_calculate_derivative_big_factor(self):
        d = self.pid._calculate_derivative(3.7, [2.0, 4.0, 6.0, 8.0, 10.0, 12.0])
        self.assertAlmostEqual(d, 7.4)

    def test_negative_derivative(self):
        d = self.pid._calculate_derivative(1.0, [12.0, 10.0, 8.0, 6.0, 4.0, 2.0])
        self.assertAlmostEqual(d, -2.0)
