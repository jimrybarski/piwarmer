from controller.runner import ProgramRunner
import logging
from logging.handlers import RotatingFileHandler

# Set up a logger for application notifications and errors
log = logging.getLogger()
handler = RotatingFileHandler('/var/log/piwarmer/heater.log', maxBytes=1024*1024*100, backupCount=5)
formatter = logging.Formatter('%(asctime)s\t%(name)s\t%(levelname)s\t\t%(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


if __name__ == "__main__":
    with ProgramRunner() as program:
        program.run()
