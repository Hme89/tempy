import pickle

# All udate frequencies in seconds between each event
data = {
"pwr": True,
"target_temp": 20,
"mode": "schedule",
"update_freq": 60*60,
"measure_freq": 10,
"temp_log_freq": 10*60,
"relay_cooldown": 60
}

outfile = open("config.pcl", "wb")
pickle.dump(data, outfile, pickle.HIGHEST_PROTOCOL)
outfile.close()
