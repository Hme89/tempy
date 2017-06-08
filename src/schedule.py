import time

class Schedule:

    def __init__(self, events):
        self.events = events
        self.__target_temp = 20

    def get_target_temp(self):
        t = time.localtime()
        for event in reversed(self.events):
            if event[0] <= t.tm_wday:
                if event[1] <= t.tm_hour:
                    if event[2] <= t.tm_min:
                        print("Temp updated!")
                        self.__target_temp = event[3]
                        return self.__target_temp
        # If start of week return last target temp
        return self.__target_temp

    def print_events(self):
        for i in range(len(self.events)):
            print("Day {} at {}:{} target is {} degrees".format(self.events[i][0],
                self.events[i][1],self.events[i][2],self.events[i][3]))
