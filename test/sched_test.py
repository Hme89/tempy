from src.schedule import Schedule
import time

s = Schedule("remote/schedule")

s.load_schedule()

s.print_events()

print("Target: ",s.get_target_temp())
print("Time: ",time.localtime())
