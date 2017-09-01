import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import shutil, os
from config import log_level

class Logger:
    """Setup for rotating logging of program messages and temperature."""
    def __init__(self, name, max_bytes=2E5, backup_count=10):
        self.make_log_dir("log")

        self.log_location = "log/{}".format(name)
        self.log = logging.getLogger(name)
        self.log_level = log_level

        self.loghandler = RotatingFileHandler(self.log_location, maxBytes=max_bytes, backupCount=backup_count)
        self.log_formatter = logging.Formatter('%(asctime)s->  %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S ')


    def get_logger(self):
        self.log.setLevel(self.log_level)
        self.loghandler.setLevel(self.log_level)
        self.loghandler.setFormatter(self.log_formatter)
        self.log.addHandler(self.loghandler)

        return self.log

    def make_log_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)


    def get_warnings(self, after=0):
        return []
        lvl = ["WARNING","ERROR","CRITICAL"]
        data = []
        last = datetime.fromtimestamp(after)

        try:
            with open(self.log_location, "r") as infile:
                lines = infile.readlines()
        except FileNotFoundError:
            self.log.warning("Logfile file not found, check logging...")


        for line in lines:
            if any(l in line for l in lvl):
                if datetime.strptime(line.split(" ->")[0], "%d/%m/%Y %H:%M:%S") < last:
                    data.append(line.rstrip())
        if len(data) == 0:
            return []
        else:
            data.reverse()
            return zlib.compress( json.dumps(data).encode() )

class TempLog(Logger):
    """docstring for templog."""
    def __init__(self, name, log, max_bytes=1.5E6, backup_count=4):
        super(TempLog, self).__init__(name, max_bytes, backup_count)
        self.log_level = "DEBUG"
        self.log_formatter = logging.Formatter('%(asctime)s-> %(message)s', datefmt='%d/%m/%Y %H:%M:%S ')
        self.log = self.get_logger()
        self.parent_log = log

    def log_temp(self, time, inside, outside, target):
        self.log.info("{} ¤ Inside = {} ¤ Outside = {} ¤ Target = {}".format(
            time, inside, outside, target))
        print(time, inside, outside, target, " Was logged")


    def export_temp_log(self):
        try:
            with open(self.log_location, "r") as infile:
                lines = infile.readlines()
        except FileNotFoundError:
            self.parent_log.error("No temp logfile, check logging...")
            return []

        # Server expects (time, inside, outside, target)
        # even if one of the sensors is None
        data = []
        for line in lines:
            event = []
            linelist = line.split("¤")
            event.append( int( float( linelist.pop(0).split(">")[-1] ) ) )
            for item in linelist:
                item_str = item.split("=")[-1].strip()
                if item_str == "None": event.append(None)
                else: event.append( float(item_str) )
            data.append(event)

        if len(data) == 0:
            return []
        else:
            return data


    def rm_tmp(self):
        os.remove(self.log_location)
