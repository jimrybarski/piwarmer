import logging
import random
import os

log = logging.getLogger(__name__)


class MockGPIO(object):
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


class MockMAX31855(object):
    """ Allows testing of thermometer functionality outside of Raspberry Pi. """
    def __init__(self, *args):
        pass

    @staticmethod
    def MAX31855(*args):
        # This is a hack to get around how the real module is structured
        return MockMAX31855()

    def readTempC(self):
        # You can set the temperature through an environment variable to test it live,
        # or if you don't care about the value it will pick a random one for you
        temp = os.getenv('MOCKTEMP', random.randint(20, 155))
        log.debug("Fake temperature: %s C" % temp)
        return temp
