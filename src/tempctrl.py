# import GPIOEmu as GPIO    # dummy GPIO library for testing
import RPi.GPIO as GPIO

import time
import pickle
from src.schedule import Schedule
from src.logger import Logger


class TempCtrl:

    def __init__(self):
        # Options
        self.heater_pin = 27
        self.sensor_id = {"inside":"28-021564920bff",}
        self.last_on = 0                   # Last time oven was on
        self.schedule = Schedule("remote/schedule")
        self.logger = Logger()
        self.config = self.load_remote_values()


        # Setup gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heater_pin, GPIO.OUT, initial=1)


    def __del__(self):
        GPIO.cleanup()

    def load_remote_values(self):
        with open("remote/config.pcl", "rb") as infile:
            values = pickle.load(infile)
        try:
            self.pwr = values["pwr"]
            self.target_temp = values["target_temp"]
            self.mode = values["mode"]
            self.update_freq = values["update_freq"]        # time beteen remote updates
            self.measure_freq = values["measure_freq"]        # time beteen remote updates
            self.temp_log_freq = values["temp_log_freq"]        # time beteen remote updates
            self.relay_cooldown = values["relay_cooldown"]  # Turn on oven max every n seconds
        except:
            self.logger.log.warning("Bad config file, using old...: ",exc_info = True )
        return values

    def update(self):
        self.load_remote_values()
        self.schedule.load_schedule()
        self.logger.log.info("Loaded remote values and updated local values")

    # Heater status  ON / OFF
    def set_heater(self, status):
        if self.pwr:
            if status == "ON":
                GPIO.output(self.heater_pin, 0)
            elif status == "OFF":
                GPIO.output(self.heater_pin, 1)
            else:
                self.logger.log.error("Invalid heater status: : %s",status)
                self.turn_off()


    def get_temp(self, sensor="inside"):
        # # Read temp from file w1

        try:
            infile =  open("/sys/bus/w1/devices/{}/w1_slave".format(self.sensor_id[sensor]), "r")
            temp = float(infile.readlines()[1].split("=")[1])/1000.
            infile.close()
            return temp
        except Exception:
            err = "Temperature sensor '{}' failure, turning off..\n".format(sensor)
            self.logger.log.error(err, exc_info = True)
            self.turn_off()


    def get_target(self):
        if self.mode == "target":
            return self.target_temp

        elif self.mode == "schedule":
            return self.schedule.get_target_temp()

        else:
            err = "Invalid mode {}: using target...\n".format(self.mode)
            self.logger.log.warning(err, exc_info = True)
            return self.target_temp


    def status(self):
        # Return current heating status and temp ect.
        print("""\nStatus of config values
        pwr            {}
        target_temp    {}
        mode           {}
        update_freq    {}
        measure_freq   {}
        temp_log_freq  {}
        relay_cooldown {}
        """.format(self.pwr, self.target_temp, self.mode, self.update_freq,
        self.measure_freq, self.temp_log_freq, self.relay_cooldown))


    def start(self):
        self.logger.log.debug("Tries to start...")

        while self.pwr:
            inside_temp = self.get_temp("inside")
            current_target_temp = self.get_target()

            # If off but should be on and not on cooldown: turn on
            if inside_temp < current_target_temp:
                if GPIO.input(self.heater_pin) == 1 and time.time() > \
                self.last_on + self.relay_cooldown:
                    self.set_heater("ON")

            # If should be off but on: turn off and update last on time
            else:
                if GPIO.input(self.heater_pin) == 0:
                    self.set_heater("OFF")
                    self.last_on = time.time()

            self.logger.log.debug("Running with oven {} : t_in: {} : t_target: {}".format(
                "on" if GPIO.input(self.heater_pin) == 0 else "off",
                inside_temp, current_target_temp))

            time.sleep(self.measure_freq)


    def log_temp(self):
        temp_inside = self.get_temp("inside")
        # temp_inside = self.get_temp("outside")
        self.logger.templog.info("{} : Inside = {} : Outside = {}".format(
            time.time(), temp_inside, 0))

    def turn_off(self):
        self.logger.log.warning("Turning off and writes to pcl... ")
        self.pwr = False
        self.set_heater(0)
        self.last_on = time.time()

        # Switch system off, so it does not restart automaticallly
        self.config["pwr"] = False
        with open("remote/config.pcl", "wb") as outfile:
            pickle.dump(self.config, outfile, pickle.HIGHEST_PROTOCOL)
