"""Data-analyse Practicum 7: identificatie (EXP 13) en absorptie in aluminium (EXP 22) van 241Am.

Gebruik: python3 analyse.py   -> maakt figuren/*.png en print alle getallen voor het verslag.
"""
import os
import numpy as np
import sympy as sp
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

os.makedirs("figuren", exist_ok=True)
plt.rcParams.update({"font.family": "sans-serif", "font.size": 10, "axes.grid": True,
                     "grid.color": "0.88", "savefig.dpi": 300, "savefig.bbox": "tight"})
komma = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ","))
KLEUR = "#1D8DB0"   # KU Leuven Blue2
FIT = "#B03A2E"

# ---------------------------------------------------------------- symbolische foutenpropagatie (sympy)
mu, smu, m, N = sp.symbols("mu sigma_mu m N", positive=True)
d12 = sp.log(2) / mu
sigma_d12 = sp.simplify(sp.Abs(sp.diff(d12, mu)) * smu)               # ln2 * sigma_mu / mu^2
I_, sI_ = sp.symbols("I sigma_I", positive=True)
sigma_lnI = sp.simplify(sp.diff(sp.log(I_), I_) * sI_)                # sigma_I / I
print("sigma_d12 =", sigma_d12, "| sigma_lnI =", sigma_lnI)
f_sd = sp.lambdify((mu, smu), sigma_d12)

# ---------------------------------------------------------------- hulpfuncties
def gemiddelde(x):
    """Gemiddelde, steekproef-s en Poissonfout sqrt(m/N) op het gemiddelde."""
    x = np.asarray(x, float)
    return x.mean(), x.std(ddof=1), np.sqrt(x.mean() / len(x))

def dispersie(x):
    """Dispersietoets: D=(N-1)s^2/m ~ chi2(N-1) onder Poisson."""
    x = np.asarray(x, float)
    D = (len(x) - 1) * x.var(ddof=1) / x.mean()
    return D, stats.chi2.sf(D, len(x) - 1)

def lin_fit(x, y, sy):
    """Gewogen kleinste kwadraten y = a x + b (formularium, A..E-notatie)."""
    w = 1 / sy**2
    A, B, C, D, E = (x*w).sum(), w.sum(), (y*w).sum(), (x*x*w).sum(), (x*y*w).sum()
    De = B*D - A*A
    a, b = (E*B - C*A)/De, (D*C - E*A)/De
    sa, sb, cov = np.sqrt(B/De), np.sqrt(D/De), -A/De
    chi2 = (((y - a*x - b)/sy)**2).sum()
    nu = len(x) - 2
    return dict(a=a, b=b, sa=sa, sb=sb, cov=cov, chi2=chi2, nu=nu, p=stats.chi2.sf(chi2, nu))

# ---------------------------------------------------------------- data
achtergrond = [4, 8, 6, 2, 2, 2, 6, 4, 4, 3]
exp13 = {"Lucht": [98,104,99,116,101,102,90,96,111,81], "Folie": [82,84,80,86,90,73,74,73,95,78],
         "Dik papier": [57,81,68,73,89,56,62,67,60,54], "Al 1 mm": [35,34,39,44,24,34,39,39,32,30],
         "Al 2 mm": [21,38,40,30,23,27,29,26,30,27], "Al 3 mm": [25,31,18,29,22,24,23,25,30,26],
         "Al 4 mm": [25,21,23,36,31,17,23,25,22,31], "Pb 1 mm": [1,2,6,2,4,6,7,3,3,2],
         "Pb 2 mm": [3,2,4,4,4,1,4,5,1,2], "Pb 3 mm": [5,2,2,3,1,2,3,2,5,2], "Pb 4 mm": [4,5,5,5,1,4,1,3,4,2]}
s22 = np.array([0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0])
raw22 = np.array([[56,59,64,60,68],[59,59,52,59,54],[46,45,54,52,54],[48,55,53,32,55],[39,52,48,44,40],
                  [41,48,49,49,38],[44,37,44,41,41],[39,32,35,53,44],[33,37,45,43,28],[39,42,35,34,40],
                  [47,31,29,35,37],[37,39,36,31,22],[29,31,25,30,19],[32,35,29,32,27],[23,11,19,24,34],
                  [26,29,14,27,24],[24,22,23,28,21],[19,17,22,27,21],[21,19,14,26,19]], float)

# ---------------------------------------------------------------- achtergrond
ma, sa_, ema = gemiddelde(achtergrond)
Da, pa = dispersie(achtergrond)
print(f"\nACHTERGROND m_a={ma:.2f} s={sa_:.2f} s^2={sa_**2:.2f} sigma={ema:.2f}  D={Da:.2f} p={pa:.2f}")

# ---------------------------------------------------------------- EXP 13
print("\nEXP 13")
namen, Inet, sInet = [], [], []
tot_a = sum(achtergrond)
for k, v in exp13.items():
    mm, s, e = gemiddelde(v)
    I, sI = mm - ma, np.hypot(e, ema)
    z = (sum(v) - tot_a) / np.sqrt(sum(v) + tot_a)
    D, p = dispersie(v)
    namen.append(k); Inet.append(I); sInet.append(sI)
    print(f"{k:10s} m={mm:6.1f} sig={e:4.2f} rel={100*e/mm:5.1f}%  I={I:6.1f}+-{sI:4.2f}  z={z:5.1f}  D={D:5.1f} p={p:.2f}  N5%={400/mm:6.1f}")
def zpaar(a, b):
    x1, x2 = sum(exp13[a]), sum(exp13[b]); return (x1 - x2)/np.sqrt(x1 + x2)
for a, b in [("Lucht","Dik papier"),("Lucht","Folie"),("Folie","Dik papier"),("Dik papier","Al 1 mm"),("Al 1 mm","Al 4 mm")]:
    print(f"z({a} - {b}) = {zpaar(a,b):.1f}")
alpha = np.mean(exp13["Lucht"]) - np.mean(exp13["Dik papier"])
s_alpha = np.hypot(gemiddelde(exp13["Lucht"])[2], gemiddelde(exp13["Dik papier"])[2])
print(f"alpha-bijdrage = {alpha:.1f} +- {s_alpha:.1f}")
I_pb1, s_pb1 = Inet[namen.index("Pb 1 mm")], sInet[namen.index("Pb 1 mm")]
I_al4 = Inet[namen.index("Al 4 mm")]
grens = I_pb1 + 2*s_pb1
print(f"Pb 1 mm: 2sigma-bovengrens {grens:.2f}, transmissie < {grens/I_al4:.3f}, d12(Pb) < {1/np.log2(I_al4/grens):.2f} mm")



# ---------------------------------------------------------------- EXP 22
print("\nEXP 22")
m22 = raw22.mean(1); sm22 = np.sqrt(m22/raw22.shape[1])
I22 = m22 - ma; sI22 = np.hypot(sm22, ema)
chi_pool = (((raw22 - m22[:, None])**2) / m22[:, None]).sum(); nu_pool = raw22.size - len(m22)
print(f"gepoolde dispersie chi2={chi_pool:.1f} nu={nu_pool} p={stats.chi2.sf(chi_pool, nu_pool):.2f}")
for s, a, b, c, d in zip(s22, m22, sm22, I22, sI22):
    print(f"s={s:3.1f} m={a:5.1f}+-{b:4.2f} ({100*b/a:4.1f}%) I={c:5.1f}+-{d:4.2f} ({100*d/c:4.1f}%)")
y, sy = np.log(I22), sI22/I22

# een exponentiele functie over alles: lineaire fit op ln I
f1 = lin_fit(s22, y, sy)
print(f"1 exp (lineaire fit ln I, alle punten): chi2={f1['chi2']:.1f} nu={f1['nu']} p={f1['p']:.4f}")

# harde component, verschillende ondergrenzen
print("smin-scan harde component:")
for smin in [0.5, 0.7, 1.0, 1.5, 2.0]:
    k = s22 >= smin - 1e-9; r = lin_fit(s22[k], y[k], sy[k])
    print(f"  smin={smin:3.1f} n={k.sum():2d} mu={-r['a']:.3f}+-{r['sa']:.3f} I0={np.exp(r['b']):.1f} chi2={r['chi2']:.1f}/{r['nu']} p={r['p']:.2f}")
SMIN = 1.0
k = s22 >= SMIN - 1e-9
H = lin_fit(s22[k], y[k], sy[k]); mu60, smu60 = -H["a"], H["sa"]
print(f"HARD: mu60={mu60:.4f}+-{smu60:.4f} lnI0={H['b']:.3f}+-{H['sb']:.3f} I0={np.exp(H['b']):.1f} "
      f"chi2={H['chi2']:.2f}/{H['nu']} p={H['p']:.2f} d12={np.log(2)/mu60:.2f}+-{f_sd(mu60, smu60):.2f} mm")

# zachte component: aftrekken van de geextrapoleerde harde component
z = ~k
ss = s22[z]
ext = np.exp(H["b"] + H["a"]*ss)
var_ln = ss**2*H["sa"]**2 + H["sb"]**2 + 2*ss*H["cov"]
sext = ext*np.sqrt(var_ln)
I27 = I22[z] - ext; sI27 = np.hypot(sI22[z], sext)
for q in zip(ss, ext, sext, I27, sI27):
    print("  s=%.1f ext=%.1f+-%.1f I27=%.1f+-%.1f" % q)
Z = lin_fit(ss, np.log(I27), sI27/I27); mu27, smu27 = -Z["a"], Z["sa"]
print(f"ZACHT: mu27={mu27:.2f}+-{smu27:.2f} I0={np.exp(Z['b']):.1f} chi2={Z['chi2']:.2f}/{Z['nu']} p={Z['p']:.3f} "
      f"d12={np.log(2)/mu27:.3f}+-{f_sd(mu27, smu27):.3f} mm")
k6 = ss <= 0.6 + 1e-9
Z6 = lin_fit(ss[k6], np.log(I27[k6]), sI27[k6]/I27[k6]); print(f"  (tot 0,6 mm: mu27={-Z6['a']:.2f}+-{Z6['sa']:.2f})")

# controle: simultane fit met twee exponentiele functies (niet-lineaire LS)
from scipy.optimize import curve_fit
twee = lambda s, A1, m1, A2, m2: A1*np.exp(-m1*s) + A2*np.exp(-m2*s)
po, pc = curve_fit(twee, s22, I22, p0=[20, 2, 37, 0.17], sigma=sI22, absolute_sigma=True)
pe = np.sqrt(np.diag(pc)); c2 = (((I22 - twee(s22, *po))/sI22)**2).sum()
print(f"2 exp: mu_z={po[1]:.2f}+-{pe[1]:.2f} mu_h={po[3]:.3f}+-{pe[3]:.3f} chi2={c2:.1f}/{len(s22)-4} p={stats.chi2.sf(c2, len(s22)-4):.2f}")

# vergelijking met EXP 13 bij dezelfde diktes
for t in [1, 2, 3, 4]:
    i13 = namen.index(f"Al {t} mm"); i22 = int(np.argmin(abs(s22 - t)))
    print(f"Al {t} mm: EXP13 {Inet[i13]:.1f}+-{sInet[i13]:.1f} EXP22 {I22[i22]:.1f}+-{sI22[i22]:.1f} "
          f"z={(Inet[i13]-I22[i22])/np.hypot(sInet[i13], sI22[i22]):.2f}")

# literatuur (NIST mu/rho [cm^2/g], log-log interpolatie), rho_Al = 2,699 g/cm^3
def loglog(E, E1, m1, E2, m2): return m1*np.exp(np.log(m2/m1)*np.log(E/E1)/np.log(E2/E1))
lit = {"59,5 keV": loglog(59.54, 50, .3681, 60, .2778), "26,3 keV": loglog(26.34, 20, 3.441, 30, 1.128),
       "17,8 keV": loglog(17.8, 15, 7.955, 20, 3.441), "13,9 keV": loglog(13.9, 10, 26.23, 15, 7.955)}
print("\nLITERATUUR")
for E, mr in lit.items():
    mul = mr*2.699/10
    ref, sref = (mu60, smu60) if E.startswith("59") else (mu27, smu27)
    zz = (ref - mul)/sref
    print(f"{E}: mu/rho={mr:.3f} mu={mul:.4f}/mm d12={np.log(2)/mul:.2f} mm  z={zz:.1f} p={2*stats.norm.sf(abs(zz)):.4f}")
print(f"Pb 59,5 keV: d12 = {np.log(2)/(5.021*11.35/10):.3f} mm")

# ---------------------------------------------------------------- figuur EXP 22 (twee panelen)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.1))
ax1.errorbar(s22[k], y[k], yerr=sy[k], fmt="o", ms=3.5, color=KLEUR, capsize=2, label="data (netto)")
xx = np.linspace(SMIN, 5.2, 50); ax1.plot(xx, H["b"] + H["a"]*xx, color=FIT, label=r"fit ($s \geq 1{,}0$ mm)")
#xx = np.linspace(0, SMIN, 20); ax1.plot(xx, H["b"] + H["a"]*xx, color=FIT, ls="--", label="extrapolatie")
ax1.set_xlabel("dikte aluminium $s$ [mm]"); ax1.set_ylabel(r"$\ln I$  ($I$ in tellingen/10 s)")
ax1.set_xlim(0.91, 5.4); ax1.set_ylim(2.1, 4)
ax1.legend(frameon=False, fontsize=8); ax1.set_title("(a)", loc="left", fontsize=10)
ax2.errorbar(ss, np.log(I27), yerr=sI27/I27, fmt="s", ms=3.5, color="#2E7D32", capsize=2, label="zachte component")
xx = np.linspace(0, 0.9, 20); ax2.plot(xx, Z["b"] + Z["a"]*xx, color=FIT, label="fit")
ax2.set_xlabel("dikte aluminium $s$ [mm]"); ax2.set_ylabel(r"$\ln I_{27}$  ($I_{27}$ in tellingen/10 s)")
ax2.legend(frameon=False, fontsize=8); ax2.set_title("(b)", loc="left", fontsize=10)
for ax in (ax1, ax2):
    ax.xaxis.set_major_formatter(komma); ax.yaxis.set_major_formatter(komma)
fig.tight_layout(); fig.savefig("figuren/exp22.png"); plt.close(fig)
print("\nfiguren opgeslagen in figuren/")
