from controller.runner import ProgramRunner
import logging
from logging.handlers import RotatingFileHandler

log = logging.getLogger()
handler = RotatingFileHandler('/var/temp_control/backend.log', maxBytes=1024*1024*100, backupCount=5)
formatter = logging.Formatter('%(asctime)s    %(name)s    %(levelname)s    %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    with ProgramRunner() as program:
        program.run()
