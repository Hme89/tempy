#!/usr/bin/env python
import subprocess
from threading import Thread, Timer
from src.tempctrl import TempCtrl
from config import path
import time, os

if not os.path.isfile("initialized.dat"):
    from src.firstrun import firstrun
    firstrun()

ctrl = TempCtrl()
ctrl.logger.log.info("\n\n New startup: {} \n".format(time.ctime()))
pwr_thread = Thread(target = ctrl.start)


def sync_and_start(pwr_thread):

    # Try to run, if pwr=False loop will terminate immediately
    if not pwr_thread.is_alive():
        pwr_thread = Thread(target = ctrl.start)
        pwr_thread.start()

    ctrl.get_remote_values()
    Timer(ctrl.update_freq, sync_and_start, args=(pwr_thread,)).start()
    ctrl.logger.log.info(ctrl.status())


def log_temp():
    ctrl.log_temp()
    Timer(ctrl.temp_log_freq, log_temp).start()
    ctrl.logger.log.info("Temperatures logged...")

try:
    sync_and_start(pwr_thread)
    log_temp()

except KeyboardInterrupt:
    #TODO
    #Fix and remove threads
    print("Shutdown requested...exiting")

except:
    ctrl.logger.log.critical("Unexpected error:\n",  exc_info = True)
    raise
