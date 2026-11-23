import pickle
import numpy as np
import matplotlib.pyplot as plt

FILENAME = "degelijke metingen (no AI)/sweep/m27.cylinder"

with open(FILENAME, "rb") as f:
            vals = pickle.load(f)
vals = np.array(vals)

def calc(FILENAME=FILENAME):
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
    line_size = 0.1  # cm
    flip_indexes = np.flatnonzero(np.diff(vals[2]) != 0) + 1
    flip_times = vals[3][flip_indexes]
    flip_counts = np.diff(np.searchsorted(flip_times, times_of_zeroes))

    # One period covers 4 amplitudes of travel
    amps = flip_counts * line_size / 4
    amp, amp_sdev = np.mean(amps), np.std(amps)

    print(f"flips per period: {np.mean(flip_counts):.2f}")
    print(f"amplitude:        {amp:.3f} cm +/- {amp_sdev:.3f} cm")

    print(f"period:     {period} sec +/- {period_sdev} sec")
    print(f"frequency:  {freq} Hz +/- {freq_sdev} Hz")
    return {"freq": freq, "freq_sdev": freq_sdev, "amp": amp, "amp_sdev": amp_sdev}

calc()
