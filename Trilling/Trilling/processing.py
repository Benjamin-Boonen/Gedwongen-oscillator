import pickle
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sgl
import scipy.optimize as sp

FILENAME = "9-11-with-timestamps.cylinder"

streepjes_lengte = 0.01

fig, ax = plt.subplots(3)

from scipy.ndimage import median_filter

def remove_short_pulses(signal, window=7, threshold=3.0, min_deviation=0.35):
    # original = np.asarray(signal, dtype=float)

    # baseline = median_filter(original, size=window, mode="reflect")
    # deviation = np.abs(original - baseline)
    # local_mad = median_filter(deviation, size=window, mode="reflect")

    # cutoff = np.maximum(min_deviation, threshold * 1.4826 * local_mad)
    # peaks = np.flatnonzero(deviation > cutoff)

    # cleaned = original.copy()
    # cleaned[peaks] = baseline[peaks]
    # return cleaned, peaks
    return signal, []  # Placeholder implementation; replace with actual logic if needed
with open(FILENAME, "rb") as f:
    vals = pickle.load(f)

# maak een x-data lijst op basis van centimeterstreepjes
# de x-data wordt linear ge-interpoleerd van de punten waar we over een streepje gaan
distance_clean = [[], []]
d = 0
past = vals[2][0]

for i in range(len(vals[2])):
    if past != vals[2][i]:
        d += streepjes_lengte
        distance_clean[0].append(d)
        distance_clean[1].append(vals[3][i])
        past = vals[2][i]

# we zoeken waar de maxima zijn, deze zijn op de extrema van de snelheid
# we zoeken dus een snelheid lijst, de twee element afgeleide
v_t = []
speed = []
for i in range(1, len(distance_clean[0])):
    middle_t = (distance_clean[1][i-1] + distance_clean[1][i])/2
    v_t.append(middle_t)
    dy = streepjes_lengte
    dx = abs(distance_clean[1][i] - distance_clean[1][i-1])
    v = dy/dx
    speed.append(v)

# De data moet geflipt worden na een minmum. Dit vergt dus eerst minima-detectie
minima = []
dip=False
tmp = []
n_toleration, n = 1, 0

lower_bound = np.min(speed) + 0.69
for i in range(len(speed)):
    if speed[i] <= lower_bound:
        dip=True
        tmp.append(v_t[i])
    else:
        if dip==True:
            if n > n_toleration:
                middle = np.average(tmp)
                tmp = []
                minima.append(middle)
                dip=False
                n=0
            else:
                n +=1
sign = 1
n = 0
distance_oriented = []
d=0

speed, peaks = remove_short_pulses(speed)

afwijking = speed[0]*(v_t[1] - v_t[0])
for i in range(len(speed)):
    try:
        if v_t[i] >= minima[n]:
            n += 1
            sign *= -1
    except IndexError:
        pass
    speed[i] *= sign
    dt = v_t[i] - v_t[i-1]
    d += speed[i]*dt
    distance_oriented.append(d - afwijking)

distance_oriented = sgl.detrend(distance_oriented)

def resonance_model(t, A, g, w1, phi, B, w2, d, c):
    return A*np.exp(-g*t/2)*np.cos(w1*t+phi) + B*np.cos(w2*t+d) + c

def sine_model(t, A, w, phi, c):
    return A*np.sin(w*t + phi) + c

# p0 = [0.075, 3.3, 7.9, -1.59, 0.0035, 6.65, 2.85, -0.0007]
# popt, pcov = sp.curve_fit(resonance_model, v_t, distance_oriented, p0)

lspace = np.linspace(v_t[0], v_t[len(v_t)-1], 5000)
# fitted_curve = resonance_model(lspace, *popt)

# A, g, w1, phi, B, w2, d, c = popt
# w0 = np.sqrt(w1**2 + (g/2)**2)   # natural frequency

# print(f"""
# Transient : A={A:.4g}, phase={phi:.3g} rad, decay γ={g:.4g} 1/s (τ=2/γ={2/g:.3g} s)
#             ω'={w1:.4g} rad/s, T={2*np.pi/w1:.4g} s, f={w1/(2*np.pi):.4g} Hz
# Steady    : B={B:.4g}, phase={d:.3g} rad
#             ω={w2:.4g} rad/s, T={2*np.pi/w2:.4g} s, f={w2/(2*np.pi):.4g} Hz
# Offset    : c={c:.4g}
# Derived   : ω0={w0:.4g} rad/s, Q=ω0/γ={w0/g:.4g}
#             beat period={2*np.pi/abs(w1-w2):.4g} s
# """)

p0 = [0.5, 7.9, 0, 0]

popt, pcov = sp.curve_fit(
    sine_model,
    v_t,
    distance_oriented,
    p0=p0,
    bounds=(
        [-np.inf, 0, -2*np.pi, -np.inf],
        [ np.inf, np.inf,  2*np.pi,  np.inf]
    )
)

A, w, phi, c = popt
fitted_curve = sine_model(lspace, *popt)

print(f"A={A:.4g}, ω={w:.4g} rad/s")
print(f"T={2*np.pi/w:.4g} s, f={w/(2*np.pi):.4g} Hz")
print(f"phase={phi:.3g} rad, offset={c:.4g}")

if True:
    fig1, ax1 = plt.subplots(3)
    ax1[0].plot(vals[3], vals[0])
    ax1[1].plot(vals[3], vals[1])
    ax1[2].plot(vals[3], vals[2])

#ax[0].plot(range(len(vals[2])), vals[2])
ax[0].plot(distance_clean[0], distance_clean[1])
ax[1].axhline(lower_bound, color="r")
ax[1].axhline(-lower_bound, color="r")
# for i in range(len(peaks)):
#     ax[1].axvline(v_t[peaks[i]], color="g")
ax[1].plot(v_t, speed)
#ax[2].plot(v_t, distance_oriented)
ax[2].scatter(v_t, distance_oriented, s=.3)
ax[2].plot(lspace, fitted_curve, color='r')
plt.show()