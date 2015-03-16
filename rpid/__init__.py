from itertools import cycle
import smbus
import time


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


class TemperatureController(object):
    def __init__(self):
        self._bus = smbus.SMBus(1)
        self._latest_temp = None

    def read_temperature(self):
        data = self._bus.read_i2c_block_data(0x4d, 1, 2)
        self._latest_temp = ((data[0] << 8) + data[1]) / 5.00
        return self._latest_temp


class TemperatureSetting(object):
    def __init__(self, temperature, duration_in_seconds):
        self._temperature = temperature
        self._duration = duration_in_seconds

    @property
    def temperature(self):
        return self._temperature

    @property
    def duration(self):
        return self._duration


class TemperatureProgram(object):
    def __init__(self):
        self._settings = []
        self._looping = False
        self._start = None
        self._hold_temp = None

    def set_temperature(self, temperature, duration_in_seconds):
        if not self._looping:
            setting = TemperatureSetting(temperature, duration_in_seconds)
            self._settings.append(setting)
        return self

    def repeat(self, times):
        if not self._looping:
            new_settings = []
            for i in range(times):
                for action in self._settings:
                    new_settings.append(action)
            self._settings = new_settings
        return self

    def loop_forever(self):
        self._looping = True
        return self

    def hold(self, temperature):
        self._hold_temp = temperature
        return self

    def start(self):
        self._start = time.time()

    def get_current_temperature(self):
        if self._looping:
            settings = cycle(self._settings)
        else:
            settings = self._settings
        elapsed = time.time() - self._start
        for setting in settings:
            elapsed -= setting.duration
            if elapsed < 0:
                return setting.temperature
        # The program program is over or holding at a specified temperature.
        return self._hold_temp if self._hold_temp else False


# def install(self, relay):
#     with open("/sys/class/gpio/export", "w") as f:
#         f.write(relay.number + "\n")
#     with open(relay.path("direction"), "w") as f:
#         f.write("out")
