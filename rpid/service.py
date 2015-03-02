import smbus


class RelayToggler(object):

    @staticmethod
    def initialize(relay):
        with open("/sys/class/gpio/export", "w") as f:
            f.write(relay.number + "\n")
        with open(relay.path("direction"), "w") as f:
            f.write("out")

    def on(self, relay):
        self._set(relay, 1)

    def off(self, relay):
        self._set(relay, 0)

    def _set(self, relay, value):
        assert value in (0, 1)
        with open(relay.value, "w") as f:
            f.write(value)


class TempSensor(object):
    def __init__(self):
        self._bus = smbus.SMBus(1)

    def set_current_temp(self, pid):
        data = self._bus.read_i2c_block_data(0x4d, 1, 2)
        pid.current_temp = ((data[0] << 8) + data[1]) / 5.00