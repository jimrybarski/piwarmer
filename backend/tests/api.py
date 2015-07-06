import unittest
from collections import defaultdict
from rpid.api import APIData


class MockRedis(object):
    def __init__(self):
        self.data = defaultdict(dict)

    def hdel(self, key, index):
        del(self.data[key][index])

    def hmset(self, key, data):
        assert isinstance(data, dict)
        self.data[key] = data


class MockAPIData(MockRedis, APIData):
    pass


class APITests(unittest.TestCase):
    def setUp(self):
        self.api = MockAPIData()

    def test_hmset(self):
        self.api.update_next_steps({0: "25C for 2 minutes",
                                    1: "55C for 1 hour",
                                    2: "12C for eight days",
                                    3: "99C for 1 picosecond",
                                    4: "88C for 88 years"},
                                   {0: "00:00:15",
                                    1: "00:05:00",
                                    2: "01:12:37",
                                    3: "02:25:00",
                                    4: "03:00:01"})
        self.assertEqual(len(self.api.data['next_steps']), 5)
        self.assertEqual(len(self.api.data['times_until']), 5)
        new_next_steps = {0: "25C for 2 minutes", 1: "55C for 1 hour", 2: "12C for eight days"}
        new_times_until = {0: "00:00:11", 1: "00:04:00", 2: "00:12:37"}
        self.api.update_next_steps(new_next_steps, new_times_until)
        self.assertDictEqual(self.api.data['next_steps'], new_next_steps)
        self.assertDictEqual(self.api.data['times_until'], new_times_until)
