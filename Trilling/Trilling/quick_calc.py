import pickle
import numpy as np
import matplotlib.pyplot as plt

FILENAME = "9-11-with-timestamps.cylinder"

with open(FILENAME, "rb") as f:
            vals = pickle.load(f)
vals = np.array(vals)

# CALCULATE THE PERIOD
scaled_spring_zero_line = (vals[1] - 0.5*np.ones_like(vals[1]))*2  # We schalen de perode-lijn naar [-1, 1]
zero_flip_indexes = np.where(np.gradient(scaled_spring_zero_line) == 1)[0] # We checken waar onze gradient 1 is dit duid een waarde-flip aan
zero_flip_indexes = zero_flip_indexes[1::2] # Omwille van hoe np.grad werkt geeft dit dubbele waarden --> filter de helft
times_of_zeroes = vals[3][zero_flip_indexes] # We nemen die momenten uit onze tijdsmetingen

periods = np.diff(times_of_zeroes) # De periode is het verschil (difference) tussen deze tijdsmetingen
period, period_sdev = np.average(periods), np.std(periods, ddof=0)
frequencies = 1 / periods
freq, freq_sdev = np.mean(frequencies), np.std(frequencies, ddof=0)

# CALCULATE THE AMPLITUDE

line_size = 1
small_lines = (vals[2] - 0.5*np.ones_like(vals[1]))*2  # We schalen de flip-lijn naar [-1, 1]
small_line_flips = np.gradient(small_lines)
small_line_flips_indexes = np.where(small_line_flips == 1)[0][1::2]


print(f"period:     {period} sec +/- {period_sdev} sec")
print(f"frequency:  {freq} Hz +/- {freq_sdev} Hz")
