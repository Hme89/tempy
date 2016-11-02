from glob import glob

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO, be sure to run with root privileges.")

class HeatControl(object):
    """Setup Pi for temperature reading and controll of power to
    electrical heating"""
    def __init__(self, arg):
        self.temp = NotImplemented
        self.relay_pins = [11,13]
        self.temp_pins = [7]
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_list, GPIO.OUT)
        try:
            basedir="/sys/bus/w1/devices/"
            self.temp_file = "{}/w1_slave".format(glob(basedir+"28*")[0])
        except:
            print("Make sure the correct modprobe kernel parameters have been set")

    def __del__(self):
        """Do GPIO cleanup on exit"""
        GPIO.cleanup()

    def read_temp(self):
        """Returns measured temperature in degrees celcius"""
        with open(self.temp_file, "r") as infile:
            lines = infile.readlines()
            infile.close()
        if "YES" not in lines[0]:
            print("Temperature probe not configured correctly")
            return None
        temp = float(line[1].split("t=")[1])/1000
        return temp

    def turn_off(self, relays=self.pin_list):
        """Turn off relays specified by pins in a list.
        If no agument is passed  turns off all relays"""
        GPIO.output(relays, HIGH)

    def turn_on(self, relays=self.pin_list):
        """Turn off relays specified by pins in a list.
        If no agument is passed  turns off all relays"""
        GPIO.output(relays, LOW)

    def pin_status(self, relays=self.pin_list):
        """Returns status of relays specified by pins in a list.
        If no agument is passed returns status of all pins in pin_list.
        1=ON, 0=OFF"""
        status = []
        for pin in pin_list:
            status.append(GPIO.input(pin))
