#!/usr/bin/env python
import  time
import subprocess
from threading import Thread, Timer
from src.tempctrl import TempCtrl

ctrl = TempCtrl()
ctrl.logger.log.info("\n\n New startup: {} \n".format(time.ctime()))
pwr_thread = Thread(target = ctrl.start)


def sync_and_start(pwr_thread):

    remote = "hmepisrv:/home/hme/Remotes/cabin"
    local  = "/home/hme/tempy"

    cmd1 = "rsync -tuv -e ssh --compress-level=9 {}/* {}/remote".format(remote, local)
    cmd2 = "rsync -tuv -e ssh --compress-level=9 {}/remote/config.pcl {}/config.pcl".format(local, remote)
    cmd3 = "rsync -av -e ssh --compress-level=9 {}/log {}".format(local, remote)

    try:
        subprocess.run(cmd1, shell=True, timeout=100)
        subprocess.run(cmd2, shell=True, timeout=100)
        subprocess.run(cmd3, shell=True, timeout=100)
    except subprocess.TimeoutExpired:
        ctrl.logger.log.warning("Sync timed out after 100 seconds...")
    except:
        ctrl.logger.log.error("Sync could not be completed: ", exc_info = True)
    ctrl.update()

    # Try to run, if pwr=False loop will terminate immediately
    if not pwr_thread.is_alive():
        pwr_thread = Thread(target = ctrl.start)
        pwr_thread.start()


    Timer(ctrl.update_freq, sync_and_start, args=(pwr_thread,)).start()
    ctrl.logger.log.info("Remote synced and thread initiated")
    ctrl.status()


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
