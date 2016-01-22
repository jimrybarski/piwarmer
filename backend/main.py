from device import ProgramRunner
import logging
from logging.handlers import RotatingFileHandler
from device import heater
from interface import APIInterface
from device import thermometer
import Adafruit_MAX31855.MAX31855 as MAX31855
import RPi.GPIO as GPIO

# Disable the temperature probe logger because it produces annoying and useless messages
maxlog = logging.getLogger('Adafruit_MAX31855.MAX31855')
maxlog.disabled = True

# Set up a logger for application notifications and errors
log = logging.getLogger("heater")

# We use rotating log files so that if there is a crash mid-run, we will lose the least amount possible.
# 5120 bytes is around 50 lines of log messages
handler = RotatingFileHandler('/var/log/piwarmer/heater.log', maxBytes=5120, backupCount=10000)
formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t\t%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


if __name__ == "__main__":
    api_interface = APIInterface()
    thermometer = thermometer.Thermometer(MAX31855.MAX31855(24, 23, 18))
    heater = heater.Heater(GPIO)
    with ProgramRunner(api_interface, thermometer, heater) as program:
        program.run()
