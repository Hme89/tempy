import numpy as np
import datetime
import matplotlib.pyplot as plt

logfile = "log/templog"


with open(logfile, "r") as infile:
    lines = infile.readlines()

n = len(lines)
# times = np.zeros(n)
times = []
inside_temps = np.zeros(n)
outside_temps = np.zeros(n)

for i in range(n):
    data = lines[i].split(">")[1].split(":")
    # times[i] = round( float(data[0]) )
    times.append( datetime.datetime.fromtimestamp(float(data[0])) )
    inside_temps[i] = float(data[1].split("=")[1])
    outside_temps[i] = float(data[2].split("=")[1])

print("\nEntries: ",n)
#plt.plot(times[-300:], inside_temps[-300:])
plt.plot(times, inside_temps)
plt.show()
