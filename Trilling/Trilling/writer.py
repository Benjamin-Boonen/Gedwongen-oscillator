import nidaqmx
import time
import pickle
import numpy as np

# Config
device = "cDAQ1Mod1"
line5 = "port0/line5"   # Oscillator 1
line6 = "port0/line6"   # Oscillator 2
line7 = "port0/line7"   # Amplitude sensor (for oscillator 2)

number_of_samples_per_channel = 10000
big_list = [[], [], [], []]
# Start NI-DAQmx Task

start_time = time.time()  # Record the start time
previous_time = 0  # Initialize previous time for timestamp calculation
with nidaqmx.Task() as task:
    task.di_channels.add_di_chan(f"{device}/{line5},{device}/{line6},{device}/{line7}",line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE) # maakt de communicatie met de channels op line 5,6 en 7 van het NI instrument
   
    try:
        for i in range(2):  # Adjust the range for the number of iterations you want
            vals = task.read(number_of_samples_per_channel=number_of_samples_per_channel)          # Leest de huidige waarde uit van line 5,6 en 7 en slaagt deze op in vals
            val5, val6, val7 = vals     # "unpacked" vals in verschillende variabelen
            print(val5, val6, val7)
            big_list[0].extend(val5)
            big_list[1].extend(val6)
            big_list[2].extend(val7)
            big_list[3].extend(np.linspace(previous_time, time.time() - start_time, number_of_samples_per_channel))
            previous_time = time.time() - start_time  # Update the previous time for the next iteration



    except KeyboardInterrupt:
        with open(f"sensor_data{time.strftime('%Y-%m-%d_%H-%M-%S')}.cylinder", "wb") as f:
            pickle.dump(big_list, f)
        print("Stopped by user.")

with open(f"sensor_data{time.strftime('%Y-%m-%d_%H-%M-%S')}.cylinder", "wb") as f:
    pickle.dump(big_list, f)