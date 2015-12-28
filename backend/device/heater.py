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
        """
        Turn on one of two pins necessary to heat the heater cartridge. This one is turned on the entire time a program is running.

        """
        self._gpio.output(Heater.ENABLE_PIN, self._gpio.HIGH)

    def disable(self):
        """
        Turn off a pin that is required for the heater cartridge to be heated.

        """
        try:
            self._gpio.output(Heater.ENABLE_PIN, self._gpio.LOW)
        except Exception:
            log.critical("DANGER! COULD NOT DEACTIVATE HEATER! UNPLUG IT IMMEDIATELY!")
            log.exception("Could not deactivate heater!")
            Heater.DANGER = True
        # This next step may fail, but we've already turned off the heater so there's no danger worth reporting.
        self._gpio.output(Heater.PWM_PIN, self._gpio.LOW)

    def heat(self, duty_cycle):
        """
        Turn on the heater for some percentage of one second.

        :param duty_cycle:    the percentage of time the heater should be active, from 0 to 100
        :type duty_cycle:    float

        """
        on_time, off_time = self._calculate_pwm(duty_cycle)
        if on_time:
            # don't want to rapidly switch this pin on and then off unless we need to
            self._gpio.output(Heater.PWM_PIN, self._gpio.HIGH)
            time.sleep(on_time)
        self._gpio.output(Heater.PWM_PIN, self._gpio.LOW)
        time.sleep(off_time)

    def _calculate_pwm(self, duty_cycle):
        """
        We do pulse-width modulation with a frequency of one Hertz, since the materials we use have such a high
        heat capacity that anything faster won't make a difference. Here we just convert duty cycle to a float
        essentially.

        :param duty_cycle:    the percentage of time the heater should be active, from 0 to 100
        :type duty_cycle:    float

        :return:    percentage of one second to heat, percentage of one second to deactivate the heater
        :rtype:     (float, float)

        """
        assert 0 <= duty_cycle <= 100
        on_time = duty_cycle / 100.0
        return on_time, 1.0 - on_time
