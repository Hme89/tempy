import GPIOEmu as GPIO    # dummy GPIO library for testing
#import RPi.GPIO as GPIO
from urllib.parse import urljoin
#from src.crypto import decrypt_server_info
import json
import threading
from src.logger import Logger
import config
import time, requests
import sys

class TempCtrl:

    def __init__(self):
        # Options
        self.heater_pins = config.heater_pins
        self.sensors_id = config.sensors_id
        self.scheduled_events = []
        self._sched_target = 20
        self.logger = Logger()
        self.last_on = 0
        self.temps = {"inside":20,"outside":20}
        self.running = False
        self.failed = False

        # Default values
        self.pwr = False
        self.target_temp = 20
        self.mode = 0                    # 0:target, 1:schedule
        self.update_freq = 20         # time beteen remote updates
        self.measure_freq = 10           # time beteen temperature measurements
        self.temp_log_freq = 60       # time temperature logging
        self.relay_cooldown = 60*5       # Turn on oven max every n seconds

        # Setup gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heater_pins, GPIO.OUT, initial=1)


    def __del__(self):
        GPIO.cleanup()


    def pull_remote_values(self):
        try:
            #TODO keys
            payload = {'key': config.key}
            url = urljoin(config.info_url, config.uid)
            values = requests.post(url, data=payload).text

            if values == "None":
                self.logger.log.info("No new updates availible, skipping...")
                return
            elif values == "kill":
                self.logger.log.critical("Killed by remote!")
                self.turn_off()
                return
            values = json.loads(values)
        except:
            self.logger.log.warning("Connection error: Could not pull updates...: ")
            return
        try:
            keys = ["pwr","target_temp","mode","update_freq","measure_freq",
            "temp_log_freq", "relay_cooldown", "scheduled_events"]
            for key in values:
                if key in keys:
                    self.logger.log.debug("Applying update: {} = {}".format(key, values[key]))
                    exec("self.{0} = values['{0}']".format(key))

            self.logger.log.info("Applying update: {} ".format(values))

        except:
            self.logger.log.warning("Bad config file, using default...: ",exc_info = True )


    def push_temp_values(self):
        pass


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


    def read_temps(self):
        # Read temp from file w1
        #self.turn_off()
        return 20


        for sensor in self.sensors_id:
            try:
                infile =  open("/sys/bus/w1/devices/{}/w1_slave".format(self.sensors_id[sensor]), "r")
                temp = float(infile.readlines()[1].split("=")[1])/1000.
                infile.close()
                self.temps[sensor] = temp
                self.logger.log.debug("New temperatures read")
            except KeyboardInterrupt:
                raise
            except Exception:
                err = "Temperature sensor '{}' failure, turning off..\n".format(sensor)
                self.logger.log.error(err, exc_info = True)
                self.turn_off()


    def get_target(self):
        # Mode 0 = target, Mode 1 = sechedule
        if self.mode == 0:
            return self.target_temp


        elif self.mode == 1:
            t = time.localtime()
            for event in reversed(self.scheduled_events):
                if event[0] <= t.tm_wday:
                    if event[1] <= t.tm_hour:
                        if event[2] <= t.tm_min:
                            self.__target_temp = event[3]
                            return self._sched_target
            # If start of week return last target temp
            return self._sched_target


    def log_temp(self):
        self.logger.templog.info("{} : Inside = {} : Outside = {} : Target = {}".format(
        time.time(), self.temps["inside"], self.temps["outside"], self.get_target()))


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


    def run(self):

        def timed_thread(func, cd):
            if not self.failed:
                    threading.Timer(cd, func).start()

        def update():
            self.pull_remote_values()
            self.push_temp_values()
            timed_thread(update, self.update_freq)

        def lt():
            self.log_temp()
            self.logger.log.debug("Temperatures logged...")
            timed_thread(lt, self.temp_log_freq)

        def power():
            current_target_temp = self.get_target()
            self.read_temps()

            # If off but should be on and not on cooldown: turn on
            if self.temps["inside"] < current_target_temp:
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

            self.logger.log.debug("Power {} : t_in: {} : t_target: {}".format(
                "on" if GPIO.input(self.heater_pins[0]) == 0 else "off",
                self.temps["inside"], current_target_temp))

            timed_thread(power, self.measure_freq)

        if not self.running:
            update()
            lt()
            power()
            self.running = True


    def turn_off(self):
        self.logger.log.warning("Turning off...")
        self.pwr = False
        self.failed = True
        self.last_on = time.time()
        self.set_heater("OFF")
        for i in threading.enumerate()[1:]:
            i.join()
        self.set_heater("OFF")
        GPIO.cleanup()
