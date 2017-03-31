import logging
from logging.handlers import RotatingFileHandler
import os

class Logger:
    """Setup for rotating logging of program messages and temperature."""
    def __init__(self):

        self.make_log_dir("log")

        self.templog = logging.getLogger("Rotating temperature log")
        self.log = logging.getLogger("Rotating log")

        self.templog.setLevel(logging.INFO)
        self.log.setLevel(logging.DEBUG)

        temphandler = RotatingFileHandler("log/templog", maxBytes=25E6, backupCount=10)
        loghandler = RotatingFileHandler("log/log", maxBytes=1E6, backupCount=2)
        log_formatter = logging.Formatter('%(asctime)s->  %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S ')
        temp_formatter = logging.Formatter('%(asctime)s-> %(message)s', datefmt='%d/%m/%Y %H:%M:%S ')
        temphandler.setLevel(logging.DEBUG)
        loghandler.setLevel(logging.DEBUG)
        temphandler.setFormatter(temp_formatter)
        loghandler.setFormatter(log_formatter)

        self.templog.addHandler(temphandler)
        self.log.addHandler(loghandler)

    def make_log_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
