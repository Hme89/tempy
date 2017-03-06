import time
import traceback, sys
from subprocess import Popen, PIPE
from src.tempctrl import TempCtrl

ctrl = TempCtrl()
# sync_cmd = ["rclone", "copy", "gdrive:TemPy", "remote/"]
# sync_freq = 4*3600
sync_cmd = ["echo", "'Hello World'"]
sync_freq = 15

try:
    while True:
        with Popen(sync_cmd, stdout=PIPE) as proc:
            print(proc.stdout.read())

        #if not TempCtrl.on:
        with open("remote/target", "r") as infile:
            pwr = [line for line in infile if line[0] != "#"][0].strip()
            print(pwr == "on")
            print(pwr)
            print(ctrl.on)

            if pwr  == "on" and not ctrl.on:
                print("Starting")
                ctrl.start()

            if pwr == "off" and ctrl.on:
                ctrl.mode = "off"

            infile.close()

        print("Going to sleep...")
        time.sleep(sync_freq)


    # TODO
    # What if shutdown?
    # Restart?
    # sync remote
    # sync log
    # logging with custom interval (move out of tempctrl)
    #

except KeyboardInterrupt:
    print("Shutdown requested...exiting")


except Exception:
    traceback.print_exc(file=sys.stdout)
    sys.exit(0)
