import GPIOEmu as GPIO    # dummy GPIO library for testing
# import RPi.GPIO as GPIO
from urllib.parse import urljoin

from src.crypto import decrypt_server_info
from src.schedule import Schedule
from src.logger import Logger
import config

import time, requests, json

class TempCtrl:

    def __init__(self):
        # Options
        self.heater_pins = config.heater_pins
        self.sensors_id = config.sensors_id
        self.schedule = Schedule(None)
        self.logger = Logger()
        self.last_on = 0                # Last time oven was on

        # Default values
        self.pwr = False
        self.target_temp = 20
        self.mode = "target"
        self.update_freq = 60*60        # time beteen remote updates
        self.measure_freq = 10          # time beteen temperature measurements
        self.temp_log_freq = 60*5       # time temperature logging
        self.relay_cooldown = 60*5      # Turn on oven max every n seconds

        self.get_remote_values()

        # Setup gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heater_pins, GPIO.OUT, initial=1)


    def __del__(self):
        GPIO.cleanup()

    def get_remote_values(self):
        try:
            enc_values = requests.get( urljoin(config.info_url, config.uid) ).txt
            values = decrypt_server_info(enc_values, config.key)
        except:
            self.logger.log.warning("Could not pull updates...: ",exc_info = True )
            return

        try:
            keys = ["pwr","target_temp","mode","update_freq","measure_freq",
            "temp_log_freq", "relay_cooldown", "schedule"]
            for key in values:
                if key in keys:
                    eval("self.{0} = values['{0}']".format(key))
        except:
            self.logger.log.warning("Bad config file, using default...: ",exc_info = True )
            print("Bad config file, using default...")


    # Heater status  ON / OFF
    def set_heater(self, status):
        if self.pwr:
            if status == "ON":
                GPIO.output(self.heater_pins, 0)
            elif status == "OFF":
                GPIO.output(self.heater_pins, 1)
            else:
                self.logger.log.error("Invalid heater status: : %s",status)
                self.turn_off()


    def get_temp(self, sensor="inside"):
        # # Read temp from file w1
        return 20

        try:
            infile =  open("/sys/bus/w1/devices/{}/w1_slave".format(self.sensors_id[sensor]), "r")
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


    def status(self):
        # Return current heating status and temp ect.
        return("""\nStatus of config values
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

        while self.pwr and not self.failed():
            inside_temp = self.get_temp("inside")
            current_target_temp = self.get_target()

            # If off but should be on and not on cooldown: turn on
            if inside_temp < current_target_temp:
                if GPIO.input(self.heater_pins[0]) == 1:
                    if time.time() > self.last_on + self.relay_cooldown:
                        self.set_heater("ON")
                        self.logger.log.debug("Turning on...")
                    else:
                        self.logger.log.debug("Relay on cooldown, waiting...")

            # If should be off but on: turn off and update last on time
            else:
                if GPIO.input(self.heater_pins[0]) == 0:
                    self.logger.log.debug("Turning off...")
                    self.set_heater("OFF")
                    self.last_on = time.time()

            self.logger.log.debug("Running with oven {} : t_in: {} : t_target: {}".format(
                "on" if GPIO.input(self.heater_pins[0]) == 0 else "off",
                inside_temp, current_target_temp))

            time.sleep(self.measure_freq)


    def log_temp(self):
        temp_inside = self.get_temp("inside")
        temp_outside = 0
        #temp_outside = self.get_temp("outside")
        self.logger.templog.info("{} : Inside = {} : Outside = {} : Target = {}".format(
            time.time(), temp_inside, temp_outside, self.get_target()))

    def turn_off(self):
        self.logger.log.warning("Turning off and writes blocking file ")
        self.pwr = False
        self.set_heater("OFF")
        self.last_on = time.time()
        GPIO.cleanup()

    def failed(self):
        return False
