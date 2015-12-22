import unittest
from backend.device.pid import PID, Driver


class PIDTests(unittest.TestCase):
    def setUp(self):
        driver = Driver('test', 1.0, 1.0, 1.0, 10.0, -10.0)
        self.pid = PID(driver)

    def test_calculate_derivative_default_values(self):
        d = self.pid._calculate_derivative(1.0, self.pid._past_errors)
        self.assertEqual(d, 0.0)