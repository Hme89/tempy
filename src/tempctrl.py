import src.gpio_dummy as GPIO    # dummy GPIO library for testing
# try:
#     import RPi.GPIO as GPIO
# except RuntimeError:
#     print("Error importing RPi.GPIO, be sure to run with root privileges.")
import time, sys, os
from src.schedule import Schedule
import logging
from logging.handlers import RotatingFileHandler

class TempCtrl:

    def __init__(self):
        # Options
        self.on = False
        self.heater_pins= [2,3]
        self.sensor_id = {"inside":"0-000802824e58",}
        self.relay_cooldown = 300           # Turn on oven max every n seconds
        self.last_on = 0                    # Last time oven was on
        self.update_every = 10              # sleep time beteen checks
        self.schedule = Schedule("heat_schedule.txt")
        self.logger = logging.getLogger("Rotating Log")
        self.mode = "remote"

        # Setup gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heater_pins, GPIO.OUT, initial=0)
        # Setup logging
        self.logger.setLevel(logging.INFO)
        logfile = "templog"
        handler = RotatingFileHandler(logfile, maxBytes=25E6, backupCount=5)
        self.logger.addHandler(handler)

    def __del__(self):
        GPIO.cleanup()

    # Heater status  1=ON 0=OFF
    def set_heater(self, status):
        if self.on:
            if status == 1:
                GPIO.output(heater_pins, 1)
            elif status == 0:
                GPIO.output(heater_pins, 0)
            else:
                print("Invalid heater status: {}".format(status))


    def get_temp(self, sensor="inside"):

        # DUMMMY function
        infile = open("dummy_temp","r")
        t = float(infile.read())
        infile.close()
        self.logger.info("{}:{}".format(time.time(), t))
        return t

        # Read temp from file w1
        try:
            infile =  open("/sys/bus/w1/devices{}/w1_slave".format(sensor_id[sensor]), "r")
            temp = float(infile.readlines()[1].split("="))/1000.
            infile.close()
        except:
            print("Temperature sensor '{}' failure, turning off..".format(sensor))
            self.on = False

        # Log the temperature
        logger.info("{} : {} : power on = {}".format(time.time, temp, self.on))
        return temp


    def status(self):
        #TODO
        # Return current heating status and temp ect.
        None


    def start(self):
        self.on = True
        while self.on:
            measured_temp = self.get_temp("inside")

            # Find target temperature
            if self.mode == "remote":
                with open("remote/target", "r") as infile:
                    target_temp = float(infile.readline())
                    infile.close()

            elif self.mode == "schedule":
                target_temp = self.schedule.get_target_temp()

            else:
                print("Unknown mode: {}\nShutting off...".format(self.mode))
                self.on = False
                return


            # If off but should be on and not on cooldown: turn on
            if measured_temp < target_temp:
                if GPIO.input(self.heater_pins) != 1 and time.time() > \
                self.last_on + self.relay_cooldown:
                    self.set_heater(1)

            # If should be off but on: turn off and update last on time
            else:
                if GPIO.input(self.heater_pins) == 1:
                    self.set_heater(0)
                    self.last_on = time.time()

            # sleep
            time.sleep(self.update_every)
