"""Prepare the forcing files of the shallow-lake and stratified-lake eutrophication examples.

Usage (from the examples/ folder of the OpenHydroQual-Examples repository):
    python shallow-lake-eutrophication/results/prep.py <climate data folder> [A] [B]
The climate data folder must hold the BWI 2010 records Temp_2010.csv, Solar_2010.csv, Wind_2010.csv
(Excel serial date, value) and "Sample_Rain_Data (mm).csv" (start, end, mm).
A writes the shallow-lake files, B the stratified-lake files.
"""
import os, re, sys
import numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else "Climate_Data"
EX = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
T0 = 40179.0


def load(fn, fix_first=False):
    t, v, dropped = [], [], 0
    for i, ln in enumerate(open(os.path.join(SRC, fn))):
        ln = ln.strip()
        if not re.fullmatch(r"[-0-9.]+,[-0-9.]+", ln):
            dropped += 1
            continue
        a, b = ln.split(",")
        t.append(float(a) - T0)
        v.append(float(b))
    t, v = np.array(t), np.array(v)
    if fix_first:
        v[0] = 2.2  # the first record reads 22, a missing decimal point (neighbours read 2.2)
    o = np.argsort(t, kind="stable")
    return t[o], v[o], dropped


def hourly_mean(t, v, grid):
    """Mean of the linear interpolant over [g, g+1h), stamped at g (uniform hourly grid)."""
    fine = np.arange(grid[0], grid[-1] + 1 / 24, 1 / 240)
    vf = np.interp(fine, t, v)
    n = len(grid)
    return vf[: n * 10].reshape(n, 10).mean(axis=1)


def do_sat(T):  # same polynomial as the reaeration source in mass_transfer.json
    return 14.652 - 0.41022 * T + 0.007991 * T ** 2 - 0.000077774 * T ** 3


def write(path, t, v, fmt="%.4f"):
    with open(path, "w") as f:
        for a, b in zip(t, v):
            f.write(("%.5g," + fmt + "\n") % (a, b))


# ---------------------------------------------------------------- weather
tT, vT, dT = load("Temp_2010.csv", fix_first=True)
tS, vS, dS = load("Solar_2010.csv")
tW, vW, dW = load("Wind_2010.csv")
print("dropped (flagged) temperature rows:", dT, dS, dW)

hours = np.arange(0, 365 + 1e-9, 1 / 24)  # 0 .. 365 days, hourly (8761 points)
Tair = hourly_mean(tT, vT, hours)
SW = np.clip(hourly_mean(tS, vS, hours), 0, None)
wind = hourly_mean(tW, vW, hours) * 0.44704  # mph -> m/s
PAR = 0.45 * SW

# water temperature: exponential moving average of hourly air temperature, tau = 5 days, floor 1 C
tau = 5.0
dt = 1 / 24
Tw = np.empty_like(Tair)
Tw[0] = max(np.mean(Tair[:24 * 7]), 1.0)  # start from the first-week mean
a = dt / tau
for i in range(1, len(Tair)):
    Tw[i] = Tw[i - 1] + a * (Tair[i] - Tw[i - 1])
Tw = np.maximum(Tw, 1.0)
days = np.arange(0, 366)
Tw_d = np.interp(days, hours, Tw)
# ice cover: assumed whenever the hourly water temperature is below 1.5 C (it sits at the 1 C floor).
# Under ice and snow 10% of PAR reaches the water and the wind does not act on the surface.
ice = Tw < 1.5
PAR = np.where(ice, 0.1 * PAR, PAR)
wind = np.where(ice, 0.0, wind)
print("ice-covered hours: %d (%.1f days); ice days:" % (ice.sum(), ice.sum() / 24), sorted(set(np.floor(hours[ice]).astype(int)))[:5], "...")
print("air T: mean %.2f min %.2f max %.2f" % (Tair.mean(), Tair.min(), Tair.max()))
print("water T daily: mean %.2f min %.2f max %.2f (day %d)" % (Tw_d.mean(), Tw_d.min(), Tw_d.max(), Tw_d.argmax()))
print("SW mean %.1f max %.1f ; PAR mean %.1f; wind mean %.2f max %.2f m/s" % (SW.mean(), SW.max(), PAR.mean(), wind.mean(), wind.max()))

# ---------------------------------------------------------------- rain -> inflow
r = np.loadtxt(os.path.join(SRC, "Sample_Rain_Data (mm).csv"), delimiter=",")
rain_d = np.zeros(366)
for s, e, mm in r:
    d = int(np.floor(s - T0 + 1e-9))
    if 0 <= d < 365:
        rain_d[d] += mm
print("rain total %.0f mm; days > 25 mm: %s" % (rain_d.sum(), [(int(i), round(rain_d[i], 1)) for i in np.where(rain_d > 25)[0]]))


def inflow(catchment_km2, base_mean):
    A = catchment_km2 * 1e6
    Qb = base_mean * (1 + 0.45 * np.cos(2 * np.pi * (days - 50) / 365))
    S, k, Qq = 0.0, 1.5, np.zeros(366)
    for i in range(366):
        excess = max(rain_d[i] - 5.0, 0) * 0.30 / 1000 * A  # m3 of quickflow generated
        S += excess
        Qq[i] = S / k
        S -= Qq[i]
    return Qb, Qq


def conc(Qb, Qq, Tw_d):
    phi = Qq / (Qb + Qq)
    c = dict(
        PO4=0.04 + 0.08 * phi, PIP=0.03 + 0.25 * phi, OP=0.02 + 0.08 * phi,
        NH3=0.08 + 0.20 * phi, NOx=2.00 - 0.60 * phi, ON=0.35 + 1.00 * phi,
        POC=1.5 + 6.0 * phi, O2=0.95 * do_sat(Tw_d))
    return c


def stratification(Tw_d, V_h, A_int, dz, Kmax, Kmin, T_on, ramp=5):
    """Prescribed two-layer stratification.

    Onset: first day after day 90 from which the 7-day mean epilimnion temperature stays at or above T_on for 22 days.
    During stratification the hypolimnion exchanges heat with the epilimnion only through
    K_min: dT_h/dt = Q_min/V_h (T_e - T_h), Q_min = A K_min / dz.
    Turnover: first day, at least 60 days after onset, when T_e falls to T_h + 0.5 C.
    Outside the stratified period T_h = T_e and K_z = K_max. K_z changes log-linearly over `ramp` days.
    """
    T7 = np.convolve(Tw_d, np.ones(7) / 7, mode="same")
    on = next(d for d in range(90, 340) if (T7[d:d + 22] >= T_on).all())
    Th = Tw_d.copy()
    rate = A_int * Kmin / dz / V_h
    off = 365
    for d in range(on, 365):
        Th[d + 1] = Th[d] + rate * (Tw_d[d] - Th[d])
        if d > on + 60 and Tw_d[d + 1] <= Th[d + 1] + 0.5:
            off = d + 1
            break
    Th[off:] = Tw_d[off:]
    days = np.arange(366)
    lk = np.full(366, np.log(Kmax))
    for d in days:
        if on <= d < off:
            lk[d] = np.log(Kmin)
        f_on = np.clip((d - on) / ramp, 0, 1) if d >= on - 0 else 0
    # ramps
    for d in range(on, min(on + ramp, 366)):
        w = (d - on + 1) / (ramp + 1)
        lk[d] = (1 - w) * np.log(Kmax) + w * np.log(Kmin)
    for d in range(off, min(off + ramp, 366)):
        w = (d - off + 1) / (ramp + 1)
        lk[d] = (1 - w) * np.log(Kmin) + w * np.log(Kmax)
    print("stratification onset day %d, turnover day %d" % (on, off))
    return Th, np.exp(lk)


if __name__ == "__main__":
    import json
    which = sys.argv[2:] or ["A", "B"]
    # ---- example A
    if "A" in which:
        out = os.path.join(EX, "shallow-lake-eutrophication")
        os.makedirs(out, exist_ok=True)
        Qb, Qq = inflow(8.0, 9000.0)
        Q = Qb + Qq
        print("A inflow mean %.0f m3/d, max %.0f, residence %.0f d" % (Q.mean(), Q.max(), 1.25e6 / Q.mean()))
        c = conc(Qb, Qq, Tw_d)
        write(os.path.join(out, "water_temperature.csv"), days, Tw_d, "%.2f")
        write(os.path.join(out, "par.csv"), hours, PAR, "%.1f")
        write(os.path.join(out, "wind_speed.csv"), hours, wind, "%.2f")
        write(os.path.join(out, "no_light.csv"), [0, 366], [0, 0], "%.0f")
        write(os.path.join(out, "tributary_inflow.csv"), days, Q, "%.1f")
        for k, v in c.items():
            write(os.path.join(out, "tributary_%s.csv" % k), days, v, "%.4f")
        for k in ("PO4", "PIP", "OP"):
            write(os.path.join(out, "tributary_%s_50pct.csv" % k), days, c[k] / 2, "%.4f")
        TP = c["PO4"] + c["PIP"] + c["OP"]
        TN = c["NH3"] + c["NOx"] + c["ON"]
        print("A TP load %.0f kg, FW TP %.3f ; TN load %.0f kg FW TN %.3f" % ((TP * Q).sum() / 1000, (TP * Q).sum() / Q.sum(), (TN * Q).sum() / 1000, (TN * Q).sum() / Q.sum()))
    if "B" in which:
        out = os.path.join(EX, "stratified-lake-eutrophication")
        os.makedirs(out, exist_ok=True)
        Qb, Qq = inflow(28.0, 31500.0)
        Q = Qb + Qq
        V = 2.0e6 + 2.4e6
        print("B inflow mean %.0f m3/d, max %.0f, residence %.0f d" % (Q.mean(), Q.max(), V / Q.mean()))
        c = conc(Qb, Qq, Tw_d)
        A_int, dz, V_h = 3.0e5, 6.0, 2.4e6
        Th, Kz = stratification(Tw_d, V_h, A_int, dz, Kmax=10.0, Kmin=float(os.environ.get("KMIN", 0.1)),
                                T_on=float(os.environ.get("TON", 16)))
        Qmix = A_int * Kz / dz
        strat = np.where(Kz < 0.1 * Kz.max())[0]
        print("stratified days (Kz < 10%% of max): %d, first %s last %s" % (len(strat), strat[:1], strat[-1:]))
        for d in range(0, 366, 15):
            print("  day %3d Te %.1f Th %.1f Kz %.3f Qmix %.0f" % (d, Tw_d[d], Th[d], Kz[d], Qmix[d]))
        write(os.path.join(out, "water_temperature.csv"), days, Tw_d, "%.2f")
        write(os.path.join(out, "hypolimnion_temperature.csv"), days, Th, "%.2f")
        write(os.path.join(out, "vertical_exchange.csv"), days, Qmix, "%.1f")
        write(os.path.join(out, "par.csv"), hours, PAR, "%.1f")
        write(os.path.join(out, "par_hypolimnion.csv"), hours, PAR * np.exp(-1.2 * 4.0), "%.2f")
        write(os.path.join(out, "wind_speed.csv"), hours, wind, "%.2f")
        write(os.path.join(out, "no_light.csv"), [0, 366], [0, 0], "%.0f")
        write(os.path.join(out, "tributary_inflow.csv"), days, Q, "%.1f")
        for k, v in c.items():
            write(os.path.join(out, "tributary_%s.csv" % k), days, v, "%.4f")
        for k in ("PO4", "PIP", "OP"):
            write(os.path.join(out, "tributary_%s_50pct.csv" % k), days, c[k] / 2, "%.4f")
        TP = c["PO4"] + c["PIP"] + c["OP"]
        print("B TP load %.0f kg" % ((TP * Q).sum() / 1000))
