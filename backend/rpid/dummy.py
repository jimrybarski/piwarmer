import logging

log = logging.getLogger(__name__)


class FakeGPIO(object):
    """
    This exists solely so we can test things outside of the Raspberry Pi.

    """
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
