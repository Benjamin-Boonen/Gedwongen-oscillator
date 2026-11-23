import pickle
import numpy as np

FILENAME = "sensor_data2026-11-09_11-18-02.cylinder"

with open(FILENAME, "rb") as f:
            vals = pickle.load(f)
vals = np.array(vals)
print(vals)