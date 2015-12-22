from device import ProgramRunner
import logging
from logging.handlers import RotatingFileHandler
from device import heater
from interface import CurrentState
from device import thermometer
import Adafruit_MAX31855.MAX31855 as MAX31855
import RPi.GPIO as GPIO

# Disable the temperature probe logger because it produces annoying and useless messages
maxlog = logging.getLogger('Adafruit_MAX31855.MAX31855')
maxlog.disabled = True

# Set up a logger for application notifications and errors
log = logging.getLogger()
handler = RotatingFileHandler('/var/log/piwarmer/heater.log', maxBytes=1024*1024*100, backupCount=5)
formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t\t%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


if __name__ == "__main__":
    current_state = CurrentState()
    thermometer = thermometer.Thermometer(MAX31855.MAX31855(24, 23, 18))
    heater = heater.Heater(GPIO)
    with ProgramRunner(current_state, thermometer, heater) as program:
        program.run()
