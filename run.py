#!/usr/bin/env python
import time, os
if not os.path.isfile("initialized.dat"):
    from src.firstrun import firstrun
    firstrun()

from src.tempctrl import TempCtrl
from config import path

ctrl = TempCtrl()
ctrl.log.info("\n\n New startup: {} \n".format(time.ctime()))


try:
    ctrl.run()

except KeyboardInterrupt:
    print("Shutdown requested...exiting")
    ctrl.turn_off()

except:
    ctrl.log.critical("Unexpected error:\n",  exc_info = True)
    raise
