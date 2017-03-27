import pickle

# All udate frequencies in seconds between each event
data = {
"pwr": True,
"target_temp": 150,
"mode": "target",
"update_freq": 15,
"measure_freq": 5,
"temp_log_freq": 10,
"relay_cooldown": 10
}

outfile = open("config.pcl", "wb")
pickle.dump(data, outfile, pickle.HIGHEST_PROTOCOL)
outfile.close()
