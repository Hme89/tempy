import GPIOEmu as GPIO    # dummy GPIO library for testing
# try:
#     import RPi.GPIO as GPIO
# except RuntimeError:
#     print("Error importing RPi.GPIO, be sure to run with root privileges.")
import time, datetime
from src.schedule import Schedule
import logging, sys
from logging.handlers import RotatingFileHandler

class TempCtrl:

    def __init__(self):
        # Options
        self.on = False
        self.target_temp = 0
        self.heater_pin = 2
        self.sensor_id = {"inside":"0-000802824e58",}
        self.relay_cooldown = 10           # Turn on oven max every n seconds
        self.last_on = 0                   # Last time oven was on
        self.update_every = 1              # sleep time beteen checks
        self.schedule = Schedule("remote/schedule")
        self.templogger = logging.getLogger("Rotating templogger")
        self.errlogger = logging.getLogger("Rotating errlogger")
        self.mode = "remote"

        # Setup gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heater_pin, GPIO.OUT, initial=0)
        # Setup logging
        self.templogger.setLevel(logging.INFO)
        self.errlogger.setLevel(logging.INFO)
        temphandler = RotatingFileHandler("log/templog", maxBytes=25E6, backupCount=5)
        errhandler = RotatingFileHandler("log/errlog", maxBytes=2E6, backupCount=2)
        self.templogger.addHandler(temphandler)
        self.errlogger.addHandler(errhandler)


    def __del__(self):
        GPIO.cleanup()

    # Heater status  1=ON 0=OFF
    def set_heater(self, status):
        if self.on:
            if status == 1:
                GPIO.output(self.heater_pin, 1)
            elif status == 0:
                GPIO.output(self.heater_pin, 0)
            else:
                print("Invalid heater status: {}".format(status))


    def get_temp(self, sensor="inside"):

        # DUMMMY function
        infile = open("dummy_temp","r")
        t = float(infile.read())
        infile.close()
        self.templogger.info("{}:{}".format(time.time(), t))
        return t

        # Read temp from file w1
        try:
            infile =  open("/sys/bus/w1/devices{}/w1_slave".format(sensor_id[sensor]), "r")
            temp = float(infile.readlines()[1].split("="))/1000.
            infile.close()
            # Log the temperature
            templogger.info("{} : {} : power on = {}".format(time.time, temp, self.on))
            return temp
        except:
            err = "{} : Temperature sensor '{}' failure, turning off..\n{}".format(
                datetime.datetime.now(), sensor, sys.exc_info()[0],sys.exc_info()[0])
            print(err)
            self.errlogger.info(err)
            self.on = False

    def status(self):
        #TODO
        # Return current heating status and temp ect.
        None

    def update_targets(self):
        try:
            with open("remote/target", "r") as infile:
                targets = [line for line in infile if line[0] != "#"]
                infile.close()
                self.on = True if targets[0].strip() == "on" else False
                self.mode = targets[1].strip()
                if self.mode == "remote":
                    self.target_temp = int(targets[2])

                elif self.mode == "schedule":
                    self.target_temp = self.schedule.get_target_temp()

                elif self.mode != "off":
                    self.turn_off()
                    raise ValueError("Unknown mode {}".format(self.mode))

        except:
            err = "{} : Targets update failure: {}".format(
                datetime.datetime.now(), sys.exc_info()[0])
            print(err)
            self.errlogger.info(err)


    def start(self):
        self.on = True

        try:
            self.schedule.load_schedule()
        except:
            err = "{} : Schedule loading failure: {}".format(
            datetime.datetime.now(), sys.exc_info()[0])
            print(err)
            self.errlogger.info(err)

        while self.on:
            measured_temp = self.get_temp("inside")
            self.update_targets()


            # If off but should be on and not on cooldown: turn on
            if measured_temp < self.target_temp:
                if GPIO.input(self.heater_pin) != 1 and time.time() > \
                self.last_on + self.relay_cooldown:
                    self.set_heater(1)

            # If should be off but on: turn off and update last on time
            else:
                if GPIO.input(self.heater_pin) == 1:
                    self.turn_off

            # sleep
            time.sleep(self.update_every)

    def turn_off(self):
        self.on = False
        self.set_heater(0)
        self.last_on = time.time()
