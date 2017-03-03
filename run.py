from src.tempctrl import TempCtrl

ctrl = TempCtrl()

try:
    ctrl.start()

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
