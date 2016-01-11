"""
Runs the backend and supplies it with fake temperature data. This allows for functional testing of the entire process.

"""
from device import ProgramRunner
import logging
from device import heater
from interface import APIInterface
from device import thermometer
from device.mock import MockGPIO, MockMAX31855

log = logging.getLogger("heater")
handler = logging.StreamHandler()
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
