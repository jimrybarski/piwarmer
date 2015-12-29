from device import ProgramRunner
import logging
from logging.handlers import RotatingFileHandler
from device import heater
from interface import APIInterface
from device import thermometer
from device.mock import MockGPIO, MockMAX31855

# Disable the temperature probe logger because it produces annoying and useless messages
maxlog = logging.getLogger('Adafruit_MAX31855.MAX31855')
maxlog.disabled = True

# Set up a logger for application notifications and errors
log = logging.getLogger("heater")
handler = RotatingFileHandler('/var/log/piwarmer/heater.log', maxBytes=1024*1024*100, backupCount=5)
formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t\t%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


if __name__ == "__main__":
    api_interface = APIInterface()
    thermometer = thermometer.Thermometer(MockMAX31855())
    heater = heater.Heater(MockGPIO)
    with ProgramRunner(api_interface, thermometer, heater) as program:
        program.run()
