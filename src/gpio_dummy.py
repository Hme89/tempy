value = 0

def cleanup():
    print("GPIO cleanup")

def setup(pins, what, initial = 0):
    print("setup pin(s) {} as {}".format(pins,what))

def setmode(mode):
    print("Setmode {}".format(mode))

def output(pins, val):
    global value
    print("output pin(s) {} as {}".format(pins, val))
    value = val

def input(pins):
    return value

BCM = "BCM"
OUT = "out"
