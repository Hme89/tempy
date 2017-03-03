import time

class Schedule:

    def __init__(self, sched_filename):
        self.events = []
        self.target_temp = 20
        self.schedule_path = "remote/schedule"
        self.load_schedule()

    def get_target_temp(self):
        t = time.localtime()

        for event in reversed(self.events):
            if event[0] <= t.tm_wday:
                if event[1] <= t.tm_hour:
                    if event[2] <= t.tm_min:
                        self.target_temp = event[3]

        return self.target_temp

    def load_schedule(self):
        try:
            infile = open(self.schedule_path, "r")
        except:
            print("Could not load heat schedule file, using old schedule")
            return
        sched_lines = infile.readlines()[2:]
        infile.close()

        if len(sched_lines) != 7:
            print("Schedule file has Invalid format, ensure one line for each day")
            return

        self.events = []
        day = 0
        for line in sched_lines:
            scheduled_events = line.split("|")[1:]
            for event in scheduled_events:
                if "=" in event:
                    clk,tmp = event.split("=")
                    hh,mm = clk.strip().split(":")
                    self.events.append([day,int(hh),int(mm),int(tmp)])
            day += 1

    def print_events(self):
        for i in range(len(self.events)):
            print("Day {} at {}:{} target is {} degrees".format(self.events[i][0],
                self.events[i][1],self.events[i][2],self.events[i][3]))
