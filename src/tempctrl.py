from urllib.parse import urljoin
import json
import threading
from src.logger import TempLog, Logger
from src.crypto import compress
import config
import time, requests
import zlib

if config.debug:
    import GPIOEmu as GPIO    # dummy GPIO library for testing
else:
    import RPi.GPIO as GPIO

class TempCtrl:

    def __init__(self):
        # Options
        self.heater_pins = config.heater_pins
        self.sensors_id = config.sensors_id
        self.scheduled_events = []
        self._sched_target = 20
        self.logger = Logger("log")
        self.log = self.logger.get_logger()
        self.last_pushed_warnings = 0
        self.templog = TempLog("templog", self.log)
        self.last_on = 0
        self.temps = {"inside":20,"outside":0}
        self.running = False
        self.failed = False

        # Default values
        self.pwr = False
        self.target_temp = 20
        self.mode = 0                    # 0:target, 1:schedule
        self.update_freq = 30         # time beteen remote updates
        self.measure_freq = 2           # time beteen temperature measurements
        self.temp_log_freq = 6       # time temperature logging
        self.relay_cooldown = 60*5       # Turn on oven max every n seconds

        # Setup gpio
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.heater_pins, GPIO.OUT, initial=1)

        # Pull updates on fresh startup
        self.pull_remote_values(force=True)


    def __del__(self):
        GPIO.cleanup()


    def pull_remote_values(self, force=False):
        try:
            payload = {'key': config.key, "force":1 if force else 0}
            url = urljoin(config.info_url, config.uid)
            values = requests.post(url, data=payload).text

            if values == "None":
                self.log.info("No new updates availible, skipping...")
                return True
            elif values == "kill":
                self.log.critical("Killed by remote!")
                self.turn_off()
                return
            values = json.loads(values)
        except:
            self.log.warning("Connection error: Could not pull updates...: ")
            return False

        try:
            keys = ["pwr","target_temp","mode","update_freq","measure_freq",
            "temp_log_freq", "relay_cooldown", "scheduled_events"]
            for key in values:
                if key in keys:
                    self.log.debug("Applying update: {} = {}".format(key, values[key]))
                    exec("self.{0} = values['{0}']".format(key))

            self.log.info("Applying update: {} ".format(values))
            return True

        except:
            self.log.warning("Bad config file, using default...: ",exc_info = True )
            return False


    def push_temp_values(self):
        temp_data = self.templog.export_temp_log()
        warn_data = self.logger.get_warnings(after=self.last_pushed_warnings)
        if temp_data == []:# and warn_data == []:
            self.log.warning("No temperature entries to push, skipping...")
            return
        payload = {'key': config.key, 'temp_data': temp_data, "warn_data": warn_data}
        payload_bytes = compress(payload)

        try:
            url = urljoin(config.log_url, config.uid)
            ans = requests.post(url, data=payload_bytes).text
            if ans == "ok":
                self.templog.rm_tmp()
                self.last_pushed_warnings = time.time()
                self.templog = TempLog("templog", self.log)
            else:
                self.log.error("Error from server: {}".format(ans))
        except ConnectionRefusedError :
            self.log.warning("Connection error: Could not push logs...: ")
            return


    # Heater status  ON / OFF
    def set_heater(self, status):
        if status == "ON":
            GPIO.output(self.heater_pins, 0)
        elif status == "OFF":
            GPIO.output(self.heater_pins, 1)
        else:
            self.log.error("Invalid heater status: : %s",status)
            self.turn_off()


    def read_temps(self):
        if config.debug:
            return

        for sensor in self.sensors_id:
            sens_loc = "/sys/bus/w1/devices/{}/w1_slave".format(self.sensors_id[sensor])
            try:
                with open(sens_loc, "r") as infile:
                    temp = float(infile.readlines()[1].split("=")[1])/1000.
                self.temps[sensor] = temp
                self.log.debug("New temperatures read")
            except Exception:
                err = "Temperature sensor '{}' failure, turning off..\n".format(sensor)
                self.log.error(err, exc_info = True)
                self.turn_off()


    def get_target(self):
        # Mode 0 = target, Mode 1 = sechedule
        if self.mode == 0:
            return self.target_temp

        elif self.mode == 1:
            # Scheduled events: [[weekday, hour, minute, target_temp] ... ]
            t = time.localtime()
            t_hash = (t.tm_wday+1)*10000 + t.tm_hour*100 + t.tm_min
            for event in reversed(self.scheduled_events):
                if event[0] <= t_hash:
                    self._sched_target = int(event[1])
                    return self._sched_target
            # If start of week return last target temp
            return self._sched_target



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
            if self.pull_remote_values():
                self.push_temp_values()
            timed_thread(update, self.update_freq)

        def lt():
            self.templog.log_temp(time.time(), self.temps["inside"],
                self.temps["outside"], self.get_target())
            self.log.debug("Temperatures logged...")
            timed_thread(lt, self.temp_log_freq)

        def power():
            current_target_temp = self.get_target()
            self.read_temps()

            # If off but should be on and not on cooldown: turn on
            if self.temps["inside"] < current_target_temp and self.pwr:
                if GPIO.input(self.heater_pins[0]) == 1:
                    if time.time() > self.last_on + self.relay_cooldown:
                        self.set_heater("ON")
                        self.log.debug("Turning on...")
                    else:
                        self.log.debug("Relay on cooldown, waiting...")

            # If should be off but on: turn off and update last on time
            else:
                if GPIO.input(self.heater_pins[0]) == 0:
                    self.log.debug("Turning off...")
                    self.set_heater("OFF")
                    self.last_on = time.time()

            self.log.debug("Power {} : t_in: {} : t_target: {}".format(
                "on" if GPIO.input(self.heater_pins[0]) == 0 else "off",
                self.temps["inside"], current_target_temp))

            timed_thread(power, self.measure_freq)

        if not self.running:
            update()
            time.sleep(10)
            power()
            time.sleep(10)
            lt()
            self.running = True


    def turn_off(self):
        self.log.warning("Turning off...")
        self.pwr = False
        self.failed = True
        self.last_on = time.time()
        self.set_heater("OFF")
        for i in threading.enumerate()[1:]:
            i.join()
        self.set_heater("OFF")
        GPIO.cleanup()
