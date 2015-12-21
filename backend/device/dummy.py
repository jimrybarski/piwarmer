import logging
import random

log = logging.getLogger(__name__)


class FakeGPIO(object):
    """ Allows testing of heater functionality outside of Raspberry Pi. """
    OUT = 'OUT'
    IN = 'IN'
    HIGH = 1
    LOW = 0

    @staticmethod
    def output(pin, state):
        log.debug("Fake GPIO pin %s set to %s" % (pin, state))

    @staticmethod
    def setup(pin, state):
        log.debug("Fake GPIO setup pin %s to %s" % (pin, state))


class FakeMAX31855(object):
    """ Allows testing of thermometer functionality outside of Raspberry Pi. """
    def __init__(self, *args):
        pass

    @staticmethod
    def MAX31855(*args):
        return FakeMAX31855()

    def readTempC(self):
        return random.randint(20, 105)
