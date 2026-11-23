import nidaqmx
import time
import pickle

# Config
device = "cDAQ1Mod1"
line5 = "port0/line5"   # Oscillator 1
line6 = "port0/line6"   # Oscillator 2
line7 = "port0/line7"   # Amplitude sensor (for oscillator 2)

number_of_samples_per_channel = 1000
big_list = [[], [], []]
# Start NI-DAQmx Task
with nidaqmx.Task() as task:
    task.di_channels.add_di_chan(f"{device}/{line5},{device}/{line6},{device}/{line7}",line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE) # maakt de communicatie met de channels op line 5,6 en 7 van het NI instrument
   
    try:
        while True:
            vals = task.read(number_of_samples_per_channel=number_of_samples_per_channel)          # Leest de huidige waarde uit van line 5,6 en 7 en slaagt deze op in vals
            val5, val6, val7 = vals     # "unpacked" vals in verschillende variabelen
            print(val5, val6, val7)
            big_list[0].append(val5)
            big_list[1].append(val6)
            big_list[2].append(val7)


    except KeyboardInterrupt:
        with open(f"sensor_data{time.strftime('%Y-%m-%d_%H-%M-%S')}.cylinder", "wb") as f:
            pickle.dump(big_list, f)
        print("Stopped by user.")

with open(f"sensor_data{time.strftime('%Y-%m-%d_%H-%M-%S')}.cylinder", "wb") as f:
    pickle.dump(big_list, f)