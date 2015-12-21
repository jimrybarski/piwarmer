import unittest
from datetime import datetime
from device.cycle import CurrentCycle


class MockProgram(object):
    pass


class CurrentCycleTests(unittest.TestCase):
    def setUp(self):
        self.cycle = CurrentCycle()

    def test_seconds_left(self):
        self.cycle.program = MockProgram()
        self.cycle.program.total_duration = 180
        self.cycle.start_time = datetime(2015, 12, 12, 12, 11, 12)
        self.cycle.current_time = datetime(2015, 12, 12, 12, 12, 12)
        self.assertEqual(self.cycle.seconds_left, 120)

