"""Compare the base run with the 50% phosphorus-load scenario.

Run both models with the OpenHydroQual console, writing all outputs, e.g.
    OpenHydroQual-Console shallow_lake.ohq -q -o base.txt -r <resources>
    OpenHydroQual-Console shallow_lake_p_load_50pct.ohq -q -o p50.txt -r <resources>
then
    python compare_scenarios.py base.txt p50.txt <water block> <figure.png> [<second water block>]
The water block is Lake (shallow lake) or Epilimnion (stratified lake, with Hypolimnion as the second block).
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHL_C, A_PC = 25.0, 0.0244


def load(path, want):
    with open(path) as f:
        hdr = [h.strip() for h in f.readline().split(",")]
    names = [hdr[i + 1] for i in range(0, len(hdr) - 1, 2)]
    idx = {n: 2 * j + 1 for j, n in enumerate(names)}
    d = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=[0] + [idx[n] for n in want], invalid_raise=False)
    return d[:, 0], {n: d[:, k + 1] for k, n in enumerate(want)}


def series(path, b):
    w = [f"{b}_{c}:concentration" for c in ("Algae", "PO4", "PIP", "OP", "O2")]
    t, d = load(path, w)
    chl = CHL_C * d[f"{b}_Algae:concentration"]
    tp = sum(d[f"{b}_{c}:concentration"] for c in ("PO4", "PIP", "OP")) + A_PC * d[f"{b}_Algae:concentration"]
    days = np.arange(0, 365)
    i = np.floor(t).astype(int)
    do_min = np.array([d[f"{b}_O2:concentration"][i == k].min() for k in days])
    chl_d = np.array([chl[i == k].mean() for k in days])
    tp_d = np.array([tp[i == k].mean() for k in days])
    return days + 0.5, chl_d, tp_d, do_min


def main():
    base, p50, b1, fig_path = sys.argv[1:5]
    b2 = sys.argv[5] if len(sys.argv) > 5 else None
    blue, orange = "#1f6fb5", "#d9822b"
    n = 3
    fig, axs = plt.subplots(n, 1, figsize=(7.2, 8.4), dpi=150, sharex=True)
    S = {}
    for lab, p in (("Base", base), ("P load −50%", p50)):
        S[lab] = series(p, b1)
        if b2:
            S[lab + " hypo"] = series(p, b2)
    for lab, col in (("Base", blue), ("P load −50%", orange)):
        t, chl, tp, dmin = S[lab]
        axs[0].plot(t, chl, color=col, lw=1.6, label=lab)
        axs[1].plot(t, tp, color=col, lw=1.6, label=f"{lab}, {b1}")
        axs[2].plot(t, dmin, color=col, lw=1.6, label=f"{lab}, {b1}")
        if b2:
            t2, _, tp2, dmin2 = S[lab + " hypo"]
            axs[1].plot(t2, tp2, color=col, lw=1.3, ls="--", label=f"{lab}, {b2}")
            axs[2].plot(t2, dmin2, color=col, lw=1.3, ls="--", label=f"{lab}, {b2}")
    axs[0].set_ylabel(f"Chlorophyll-a, {b1} (µg/L)")
    axs[1].set_ylabel("Total phosphorus (g P/m³)")
    axs[2].set_ylabel("Daily minimum DO (g/m³)")
    axs[2].axhline(2.0, color="#7b8a9c", lw=1, ls=":")
    axs[2].annotate("Hypoxia (2 g/m³)", xy=(1, 2.0), xycoords=("axes fraction", "data"), xytext=(-4, 3),
                    textcoords="offset points", ha="right", fontsize=8, color="#4a5a6d")
    axs[2].set_xlabel("Time (days from 1 January 2010)")
    for ax in axs:
        ax.grid(True, color="#e3e8ef", lw=0.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.legend(frameon=False, fontsize=8)
    axs[0].set_title("Base run versus 50% tributary phosphorus load (daily values)", fontsize=10)
    fig.tight_layout()
    fig.savefig(fig_path)
    # summary numbers
    for lab in ("Base", "P load −50%"):
        t, chl, tp, dmin = S[lab]
        s = (t > 120) & (t < 273)
        msg = f"{lab}: {b1} chl mean May-Sep {chl[s].mean():.1f}, annual {chl.mean():.1f}, peak {chl.max():.1f}; TP mean {tp.mean():.3f}; DO min {dmin.min():.2f}"
        if b2:
            t2, _, tp2, dmin2 = S[lab + " hypo"]
            msg += f"; {b2} TP mean {tp2.mean():.3f} max {tp2.max():.3f}; days with {b2} DO<2: {(dmin2 < 2).sum()}"
        print(msg)


if __name__ == "__main__":
    main()
