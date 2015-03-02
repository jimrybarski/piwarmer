class Relay(object):
    def __init__(self, name):
        assert name in ("hot", "cold")
        numbers = {"hot": "22",
                   "cold": "27"}
        self._number = numbers[name]

    @property
    def number(self):
        return self._number

    def path(self, item):
        assert item in ("value", "direction")
        return "/sys/class/gpio/gpio%s/%s" % (self.number, item)


class PID(object):
    def __init__(self):
        self._current_temp = None

