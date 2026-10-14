#!/usr/bin/env python3
"""Parameter sweep with the OpenHydroQual console solver.

For each value in --values, this script copies the model and its input files
into its own run folder, appends one script command to the copy

    setvalue; object=<object>, quantity=<quantity>, value=<value>

runs OpenHydroQual-Console on it, reads the output file and plots one output
series for every run. A summary table (CSV) is written next to the figure.

Example (from the folder that holds column.ohq):

    python3 sweep.py --console /path/to/OpenHydroQual-Console \
                     --resources /path/to/OpenHydroQual/resources

Requires Python 3.8+ and matplotlib.
"""
import argparse
import csv
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def read_output(path):
    """Read an OpenHydroQual output file.

    The header is 't, name_1, t, name_2, ...' and every series has its own time
    column. Returns {name: (times, values)}.
    """
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    header = [h.strip() for h in lines[0].split(",")]
    names = [header[i + 1] for i in range(0, len(header) - 1, 2)]
    series = {n: ([], []) for n in names}
    for line in lines[1:]:
        cells = line.split(",")
        for j, n in enumerate(names):
            if 2 * j + 1 < len(cells):
                try:
                    t, v = float(cells[2 * j]), float(cells[2 * j + 1])
                except ValueError:
                    continue
                series[n][0].append(t)
                series[n][1].append(v)
    return series


def run_case(model, inputs, edits, workdir, console, resources):
    """Copy the model and inputs to workdir, append script commands, run, return outputs."""
    os.makedirs(workdir, exist_ok=True)
    for f in inputs:
        shutil.copy(os.path.join(HERE, f), workdir)
    text = open(os.path.join(HERE, model), encoding="utf-8").read().rstrip("\n")
    text += "\n" + "\n".join(edits) + "\n"
    target = os.path.join(workdir, os.path.basename(model))
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    cmd = [console, target, "-q", "-o", "output.txt"]
    if resources:
        cmd += ["-r", resources]
    r = subprocess.run(cmd, capture_output=True, text=True)
    with open(os.path.join(workdir, "console.log"), "w") as f:
        f.write(r.stdout + r.stderr)
    # 0 = ok, 4 = model errors, 5 = solve failed
    if r.returncode != 0:
        sys.exit(f"console exited with code {r.returncode}; see {workdir}/console.log")
    return read_output(os.path.join(workdir, "output.txt"))


def crossing_time(t, v, level):
    """First time the series rises through `level` (linear interpolation), or None."""
    for i in range(1, len(t)):
        if v[i - 1] < level <= v[i]:
            return t[i - 1] + (level - v[i - 1]) * (t[i] - t[i - 1]) / (v[i] - v[i - 1])
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="column.ohq")
    ap.add_argument("--inputs", nargs="*", default=["inflow.txt", "inflow_concentration.txt"],
                    help="input files the model reads")
    ap.add_argument("--object", default="K_D", help="object whose property is varied")
    ap.add_argument("--quantity", default="base_value", help="property that is varied")
    ap.add_argument("--values", nargs="+", type=float, default=[0.5, 1, 2, 4])
    ap.add_argument("--series", default="Cell_10_Cu_aq:concentration", help="output column to plot")
    ap.add_argument("--console", default=os.environ.get("OHQ_CONSOLE", "OpenHydroQual-Console"))
    ap.add_argument("--resources", default=os.environ.get("OHQ_RESOURCES", ""))
    ap.add_argument("--workdir", default=os.path.join(HERE, "runs"))
    ap.add_argument("--figure", default=os.path.join(HERE, "sweep.png"))
    args = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    c_in = 8.0                      # g/m3, from inflow_concentration.txt
    rows = []
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=150)
    for value in args.values:
        edits = [f"setvalue; object={args.object}, quantity={args.quantity}, value={value:g}"]
        out = run_case(args.model, args.inputs, edits,
                       os.path.join(args.workdir, f"{args.object}_{value:g}"), args.console, args.resources)
        if args.series not in out:
            sys.exit(f"'{args.series}' is not an output column; available: {', '.join(out)}")
        t, v = out[args.series]
        ax.plot(t, v, lw=1.8, label=f"{args.object} = {value:g}")
        t50 = crossing_time(t, v, 0.5 * c_in)
        rows.append({args.object: value, "t_half_rise_days": "" if t50 is None else round(t50, 2),
                     "peak": round(max(v), 4)})
        print(f"{args.object} = {value:g}: C/C0 = 0.5 reached at "
              f"{'never' if t50 is None else f'{t50:.1f} days'}, peak {max(v):.3f}")

    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Effluent Cu (g/m³)")
    ax.grid(True, color="#e3e8ef", lw=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(args.figure)

    table = os.path.splitext(args.figure)[0] + "_summary.csv"
    with open(table, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {args.figure} and {table}")


if __name__ == "__main__":
    main()
