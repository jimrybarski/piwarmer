import time
import logging

log = logging.getLogger(__name__)


class Heater(object):
    """
    Controls the pins that cause current to pass through the heating element.
    We do PWM with 1 Hz cycles, just because the libraries that implement it
    seem to not work well with Raspberry Pi B+, and because the things we're heating
    take a long time to heat or cool, so 1 Hz is fine.

    """
    PWM_PIN = 16
    ENABLE_PIN = 20
    DANGER = False

    def __init__(self, gpio):
        self._gpio = gpio
        self._gpio.setup(Heater.ENABLE_PIN, self._gpio.OUT)
        self._gpio.setup(Heater.PWM_PIN, self._gpio.OUT)

    def enable(self):
        self._gpio.output(Heater.ENABLE_PIN, self._gpio.HIGH)

    def disable(self):
        try:
            self._gpio.output(Heater.ENABLE_PIN, self._gpio.LOW)
        except Exception:
            log.critical("DANGER! COULD NOT DEACTIVATE HEATER! UNPLUG IT IMMEDIATELY!")
            log.exception("Could not deactivate heater!")
            Heater.DANGER = True
        # This next step may fail, but we've already turned off the heater so there's no danger worth reporting.
        self._gpio.output(Heater.PWM_PIN, self._gpio.LOW)

    def heat(self, duty_cycle):
        on_time, off_time = self._calculate_pwm(duty_cycle)
        self._gpio.output(Heater.PWM_PIN, self._gpio.HIGH)
        time.sleep(on_time)
        self._gpio.output(Heater.PWM_PIN, self._gpio.LOW)
        time.sleep(off_time)

    def _calculate_pwm(self, duty_cycle):
        assert 0.0 <= duty_cycle <= 100.0
        on_time = duty_cycle / 100.0
        return on_time, 1.0 - on_time
