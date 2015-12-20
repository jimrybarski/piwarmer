import time
import logging
from dummy import FakeGPIO

log = logging.getLogger(__name__)


try:
    import RPi.GPIO as GPIO
except (SystemError, ImportError):
    log.warn("Not running on Raspberry Pi, so heater is not available. Using Dummy GPIO instead.")
    GPIO = FakeGPIO


class Heater(object):
    PWM_PIN = 16
    ENABLE_PIN = 20
    DANGER = False

    def __init__(self):
        GPIO.setup(Heater.ENABLE_PIN, GPIO.OUT)
        GPIO.setup(Heater.PWM_PIN, GPIO.OUT)

    def enable(self):
        GPIO.output(Heater.ENABLE_PIN, GPIO.HIGH)

    def disable(self):
        try:
            GPIO.output(Heater.ENABLE_PIN, GPIO.LOW)
            GPIO.output(Heater.PWM_PIN, GPIO.LOW)
        except:
            log.critical("DANGER! COULD NOT DEACTIVATE HEATER! UNPLUG IT IMMEDIATELY!")
            Heater.DANGER = True

    def heat(self, duty_cycle):
        assert 0.0 <= duty_cycle <= 100.0
        on_time = duty_cycle / 100.0
        off_time = 1.0 - on_time
        GPIO.output(Heater.PWM_PIN, GPIO.HIGH)
        time.sleep(on_time)
        GPIO.output(Heater.PWM_PIN, GPIO.LOW)
        time.sleep(off_time)
