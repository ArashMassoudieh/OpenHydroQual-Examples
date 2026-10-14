#!/usr/bin/env python3
"""Build the examples site.

For every examples/<id>/README.md (YAML front matter + Markdown body):
  * render the model diagram from the .ohq canvas positions
  * optionally run the model with the OpenHydroQual console and plot results
  * write site/examples/<id>/index.html and site/downloads/<id>.zip
and regenerate site/data/catalog.json from all front matter.

Usage:
  tools/build.py [--run] [--console PATH] [--resources DIR] [ids...]
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import markdown
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from ohqlib import LAYOUT_KEYS, Model, Plugins, pretty_text, pretty_unit, split_value_unit  # noqa: E402
import diagram  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples")
SITE = os.path.join(ROOT, "site")
TRACKS = os.path.join(ROOT, "tracks.yaml")
LEVELS = ["", "Beginner", "Intermediate", "Advanced"]
CATALOG_FIELDS = ["id", "title", "track", "level", "status", "summary", "plugins", "features", "keywords", "doc"]
KIND_ORDER = [
    ("block", "Blocks", "Storage compartments: each holds water (and dissolved or particulate mass) and has a state that evolves in time."),
    ("composite", "Composite blocks", "Pre-assembled groups of blocks and links that behave as a single unit."),
    ("link", "Links", "Connections that move water (and the mass it carries) between blocks."),
    ("source", "Sources", "External inputs or sinks applied to blocks: rainfall, evaporation, loads, exchange with the atmosphere."),
    ("constituent", "Constituents", "Substances or particles carried by the water."),
    ("reaction_parameter", "Reaction parameters", "Named coefficients used in reaction rate expressions."),
    ("reaction", "Reactions", "Transformations among constituents, each with a stoichiometry and a rate expression."),
    ("parameter", "Model parameters", "Quantities flagged for estimation, with their search ranges or priors."),
    ("observation", "Observations", "Model outputs that are recorded and, when data are supplied, compared with measurements."),
    ("objectivefunction", "Objective functions", "Quantities the optimizer minimizes."),
]
SYSTEM_KEYS = [
    ("simulation_start_time", "Start time"), ("simulation_end_time", "End time"),
    ("initial_time_step", "Initial time step"), ("maximum_time_step", "Maximum time step"),
    ("write_interval", "Write interval (steps)"), ("nr_tolerance", "Newton-Raphson tolerance"),
]


def read_readme(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing YAML front matter")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def find_model(d, meta):
    if meta.get("model"):
        return os.path.join(d, meta["model"])
    ohqs = [f for f in os.listdir(d) if f.endswith(".ohq")]
    if len(ohqs) != 1:
        raise SystemExit(f"{d}: expected one .ohq (or set 'model:' in front matter), found {ohqs}")
    return os.path.join(d, ohqs[0])


def esc(s):
    return html.escape(str(s), quote=True)


def md(s):
    return markdown.markdown(s or "", extensions=["tables", "fenced_code", "sane_lists", "attr_list"])


# ---------------------------------------------------------------- results

def read_output(path):
    """Parse an OHQ output file: header 't, name1,t, name2,...' with paired columns."""
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    if not lines:
        return {}
    hdr = [h.strip() for h in lines[0].split(",")]
    names = [hdr[i + 1] for i in range(0, len(hdr) - 1, 2)]
    series = {n: ([], []) for n in names}
    for ln in lines[1:]:
        vals = ln.split(",")
        for j, n in enumerate(names):
            if 2 * j + 1 < len(vals):
                try:
                    series[n][0].append(float(vals[2 * j]))
                    series[n][1].append(float(vals[2 * j + 1]))
                except ValueError:
                    pass
    return series


def read_xy(path):
    """Two-column numeric file (comma, tab or space separated); non-numeric lines are skipped."""
    t, v = [], []
    for ln in open(path, encoding="utf-8", errors="replace"):
        parts = [x for x in re.split(r"[,\t ]+", ln.strip()) if x]
        if len(parts) < 2:
            continue
        try:
            t.append(float(parts[0]))
            v.append(float(parts[1]))
        except ValueError:
            continue
    return t, v


def make_plots(meta, series, out_dir, ex_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    palette = ["#1f6fb5", "#d9822b", "#2a9d6f", "#b8417e", "#6a55c2", "#8a6d1f", "#56606e"]
    made = []
    for i, p in enumerate(meta.get("plots", []) or []):
        fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=150)
        found = 0
        for k, s in enumerate(p.get("series", [])):
            if isinstance(s, str):
                s = {"column": s}
            color = s.get("color", palette[k % len(palette)])
            if "file" in s:  # reference data: analytical solution or observations
                fp = os.path.join(ex_dir, s["file"])
                if not os.path.exists(fp):
                    print(f"    ! plot '{p.get('title')}': file '{s['file']}' not found", file=sys.stderr)
                    continue
                t, v = read_xy(fp)
                label = s.get("label", s["file"])
            elif "columns" in s:  # sum of several outputs, e.g. total outflow
                missing = [c for c in s["columns"] if c not in series]
                if missing:
                    print(f"    ! plot '{p.get('title')}': columns {missing} not in output", file=sys.stderr)
                    continue
                t = series[s["columns"][0]][0]
                n = min(len(series[c][1]) for c in s["columns"])
                t, v = t[:n], [sum(series[c][1][i] for c in s["columns"]) for i in range(n)]
                label = s.get("label", " + ".join(s["columns"]))
            else:
                col = s["column"]
                label = s.get("label", col)
                if col not in series:
                    print(f"    ! plot '{p.get('title')}': column '{col}' not in output", file=sys.stderr)
                    continue
                t, v = series[col]
            if "scale" in s:  # unit conversion, e.g. m/day to mm/h
                v = [x * s["scale"] for x in v]
            style = s.get("style", "line")
            if style == "points":
                ax.plot(t, v, "o", ms=3.5, color=color, label=label, alpha=.85)
            elif style == "dashed":
                ax.plot(t, v, "--", color=color, lw=1.6, label=label)
            else:
                ax.plot(t, v, color=color, lw=1.8, label=label)
            found += 1
        if not found:
            plt.close(fig)
            continue
        ax.set_xlabel(p.get("xlabel", "Time (days)"))
        ax.set_ylabel(p.get("ylabel", ""))
        if p.get("logy"):
            ax.set_yscale("log")
        for h in p.get("hlines", []) or []:  # reference levels: thresholds, crests, targets
            ax.axhline(h["y"], color=h.get("color", "#7b8a9c"), lw=1, ls=":")
            if h.get("label"):
                ax.annotate(h["label"], xy=(1, h["y"]), xycoords=("axes fraction", "data"),
                            xytext=(-4, 3), textcoords="offset points", ha="right", fontsize=8, color="#4a5a6d")
        if p.get("xlim"):
            ax.set_xlim(*p["xlim"])
        if p.get("ylim"):
            ax.set_ylim(*p["ylim"])
        ax.grid(True, color="#e3e8ef", lw=0.8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        if found > 1:
            ax.legend(frameon=False, fontsize=9)
        fig.tight_layout()
        fn = f"plot_{i + 1}.png"
        fig.savefig(os.path.join(out_dir, fn))
        plt.close(fig)
        made.append((fn, p.get("title", ""), p.get("caption", "")))
    return made


def run_model(model_path, files, console, resources):
    tmp = tempfile.mkdtemp(prefix="ohqbuild_")
    for f in [model_path] + files:
        shutil.copy(f, tmp)
    m = os.path.join(tmp, os.path.basename(model_path))
    r = subprocess.run([console, m, "-q", "-o", "build_output.txt", "-r", resources],
                       capture_output=True, text=True, timeout=1800)
    out = os.path.join(tmp, "build_output.txt")
    if r.returncode != 0 or not os.path.exists(out):
        print(f"    ! console failed (rc={r.returncode}):\n{(r.stdout + r.stderr)[-1500:]}", file=sys.stderr)
        return None, r.returncode
    return read_output(out), 0


# ---------------------------------------------------------------- page parts

def props_table(o, plugins, ctypes):
    rows = []
    for k, v in o["props"].items():
        if k in LAYOUT_KEYS or v == "":
            continue
        if o["kind"] == "reaction" and (k == "rate_expression" or k.endswith(":stoichiometric_constant")):
            continue  # shown in the reaction summary
        val, unit = split_value_unit(v)
        qual = k.split(":")[0] if ":" in k else None
        # per-constituent defaults (zero inflow, no external source) are noise
        if qual and val in ("0", "") and not k.endswith(":concentration"):
            continue
        label, dunit, help_ = plugins.prop_info(o["type"], k, ctypes.get(qual))
        unit = unit or dunit
        if ":" in k:
            label = f'{k.split(":")[0]}: {label}'
        rows.append(f"<tr><td>{pretty_text(label)}</td><td class='v'>{esc(val)}</td>"
                    f"<td>{pretty_unit(unit)}</td><td>{pretty_text(help_)}</td></tr>")
    if not rows:
        return ""
    return ("<table class='props'><thead><tr><th>Property</th><th>Value</th><th>Unit</th><th>Meaning</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def reaction_block(o, constituents):
    p = o["props"]
    st = [(c, p.get(f"{c}:stoichiometric_constant", "")) for c in constituents]
    st = [(c, s) for c, s in st if s not in ("", "0")]
    rows = "".join(f"<tr><td>{esc(c)}</td><td class='v'>{esc(s)}</td></tr>" for c, s in st)
    return (f"<div class='rxn'><div class='rate'><span>Rate</span><code>{esc(p.get('rate_expression', ''))}</code></div>"
            f"<table class='props stoich'><thead><tr><th>Constituent</th><th>Stoichiometric coefficient</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div>")


def components_html(model, plugins, roles):
    constituents = [o["name"] for o in model.of_kind("constituent")]
    ctypes = {o["name"]: o["type"] for o in model.of_kind("constituent")}
    out = []
    for kind, title, blurb in KIND_ORDER:
        objs = model.of_kind(kind)
        if not objs:
            continue
        out.append(f"<h3>{title} <small>{len(objs)}</small></h3><p class='kind-blurb'>{blurb}</p><div class='comp-list'>")
        # Collapse long runs of same-typed objects that have no individual role text.
        groups = {}
        for o in objs:
            if o["name"] in roles or len([x for x in objs if x["type"] == o["type"]]) < 6:
                groups.setdefault(("one", o["name"]), []).append(o)
            else:
                groups.setdefault(("many", o["type"]), []).append(o)
        for (mode, key), members in groups.items():
            o = members[0]
            tdesc = plugins.describe(o["type"])
            plug = plugins.source.get(o["type"], "")
            role = roles.get(o["name"]) or roles.get(o["type"]) or ""
            if mode == "many":
                name = f"{len(members)} × {esc(o['type'])}"
                names = ", ".join(esc(m["name"]) for m in members[:8]) + (" …" if len(members) > 8 else "")
                body = f"<p class='members'>{names}</p><p class='muted'>Showing properties of <b>{esc(o['name'])}</b>.</p>"
            else:
                name = esc(o["name"])
                body = ""
            detail = reaction_block(o, constituents) if kind == "reaction" else ""
            detail += props_table(o, plugins, ctypes)
            out.append(
                f"<details class='comp' id='c-{esc(re.sub(r'[^A-Za-z0-9]+', '-', o['name']))}'>"
                f"<summary><span class='cname'>{name}</span><span class='ctype'>{esc(o['type'])}"
                f"{' · ' + esc(plug) if plug and plug != 'main_components' else ''}</span>"
                f"<span class='crole'>{md(role) if role else '<p>' + pretty_text(tdesc) + '</p>'}</span></summary>"
                f"<div class='cbody'>{body}{('<p class=type-help><b>' + esc(o['type']) + ':</b> ' + pretty_text(tdesc) + '</p>') if role and tdesc else ''}{detail}</div></details>")
        out.append("</div>")
    return "\n".join(out)


def page(meta, body_md, model, plugins, svg, plots, track, files, zip_name, zip_size):
    roles = meta.get("components", {}) or {}
    inputs = meta.get("inputs", {}) or {}
    color = track["color"]
    sysrows = "".join(f"<tr><td>{lbl}</td><td class='v'>{esc(model.system[k])}</td></tr>"
                      for k, lbl in SYSTEM_KEYS if model.system.get(k, "") != "")
    file_rows = "".join(
        f"<tr><td><code>{esc(os.path.basename(f))}</code></td><td>{md(inputs.get(os.path.basename(f), ''))}</td></tr>"
        for f in files)
    plot_html = "".join(
        f"<figure><img src='{fn}' alt='{esc(t)}' loading='lazy'><figcaption><b>{esc(t)}</b> {esc(c)}</figcaption></figure>"
        for fn, t, c in plots)
    doc = (f"<a class='btn ghost' href='../../docs/{esc(meta['doc'])}' target='_blank' rel='noopener'>Technical guide (PDF)</a>"
           if meta.get("doc") else "")
    dots = "".join(f"<b class='{'f' if i <= meta['level'] else ''}'></b>" for i in (1, 2, 3))
    plugin_tags = "".join(f"<a class='plug' href='../../?plugin={esc(p)}'>{esc(p)}</a>" for p in meta.get("plugins", []))
    kw = ", ".join(meta.get("keywords", []))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta['title'])} · OpenHydroQual Examples</title>
<meta name="description" content="{esc(meta['summary'])}">
<meta name="keywords" content="{esc(kw)}">
<link rel="icon" href="../../assets/ohq.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../assets/style.css"><link rel="stylesheet" href="../../assets/example.css">
</head><body style="--c:{color}">
<header class="topbar"><div class="wrap topbar-inner">
<a class="brand" href="https://openhydroqual.com"><img src="../../assets/ohq.png" alt="" width="32" height="32"><span>OpenHydroQual</span></a>
<nav class="topnav"><a href="https://openhydroqual.com">Home</a><a href="../../" aria-current="page">Examples</a>
<a href="../../#docs">Documentation</a><a href="https://github.com/ArashMassoudieh/OpenHydroQual/releases">Download</a></nav>
</div></header>
<section class="ex-hero"><div class="wrap">
<a class="crumb" href="../../">← All examples</a>
<div class="ex-track">{esc(track['name'])}</div>
<h1>{esc(meta['title'])}</h1>
<p class="lede">{esc(meta['summary'])}</p>
<div class="ex-meta"><span class="level">{dots}<span>{LEVELS[meta['level']]}</span></span>{plugin_tags}</div>
</div></section>
<main class="wrap ex-main">
<aside class="ex-side">
  <div class="dlbox">
    <a class="btn primary big" href="../../downloads/{esc(zip_name)}" download>Download model (.zip)</a>
    <div class="muted">{zip_size} · {len(files) + 1} files · open <code>{esc(os.path.basename(model.path))}</code> in OpenHydroQual and press Run</div>
    {doc}
  </div>
  <nav class="toc"><b>On this page</b>
    <a href="#overview">Overview</a><a href="#diagram">Model diagram</a><a href="#components">Components</a>
    {'<a href="#inputs">Input files</a>' if files else ''}<a href="#settings">Simulation settings</a>
    {'<a href="#results">Results</a>' if plots else ''}
  </nav>
</aside>
<article class="ex-body">
<section id="overview" class="prose">{md(body_md)}</section>
<section id="diagram"><h2>Model diagram</h2>
<div class="diagram">{svg or '<p class=muted>This model has no spatial layout.</p>'}</div>
<p class="muted">Hover a block or link to see its name and type. Arrows show the positive flow direction.</p></section>
<section id="components"><h2>Components</h2>
<p class="muted">Click a component to see every property set in the model file, with units and meaning.</p>
{components_html(model, plugins, roles)}</section>
{f'<section id="inputs"><h2>Input files</h2><table class="props files"><tbody>{file_rows}</tbody></table></section>' if files else ''}
<section id="settings"><h2>Simulation settings</h2><table class="props narrow"><tbody>{sysrows}</tbody></table></section>
{f'<section id="results"><h2>Results</h2><p class="muted">Produced by running the downloaded model unchanged.</p>{plot_html}</section>' if plots else ''}
</article></main>
<footer class="foot"><div class="wrap">OpenHydroQual is open source. This example is free to use and adapt.
<a href="https://github.com/ArashMassoudieh/OpenHydroQual-Examples/tree/main/examples/{esc(meta['id'])}">View source on GitHub</a>.</div></footer>
</body></html>"""


def human(n):
    for u in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} GB"


# ---------------------------------------------------------------- main

def build_one(eid, args, tracks):
    d = os.path.join(EX, eid)
    meta, body = read_readme(os.path.join(d, "README.md"))
    meta["id"] = eid
    if meta.get("status", "ready") != "ready":
        return meta
    model_path = find_model(d, meta)
    model = Model(model_path)
    plugins = Plugins(args.resources, model.templates)
    files = []
    for f in model.data_files():
        p = os.path.join(d, f)
        if os.path.exists(p):
            files.append(p)
        elif f not in (meta.get("ignore_files") or []):
            print(f"    ! {eid}: referenced file missing: {f}", file=sys.stderr)
    for f in meta.get("extra_files") or []:
        p = os.path.join(d, f)
        if os.path.exists(p):
            if p not in files:
                files.append(p)
        else:
            print(f"    ! {eid}: extra file missing: {f}", file=sys.stderr)
    out = os.path.join(SITE, "examples", eid)
    os.makedirs(out, exist_ok=True)
    svg, _ = diagram.render(model, plugins, args.resources, os.path.join(out, "icons"))
    if svg:
        open(os.path.join(out, "diagram.svg"), "w").write(svg)
        open(os.path.join(out, "thumb.svg"), "w").write(diagram.thumbnail(svg, os.path.join(out, "icons")))

    plots = []
    if args.run:
        series, rc = run_model(model_path, files, args.console, args.resources)
        if series is None:
            meta["_failed"] = True
        else:
            plots = make_plots(meta, series, out, d)
            if args.columns:
                print("    columns:", ", ".join(series.keys()))
    else:  # reuse previously generated plots
        plots = [(f"plot_{i + 1}.png", p.get("title", ""), p.get("caption", ""))
                 for i, p in enumerate(meta.get("plots", []) or [])
                 if os.path.exists(os.path.join(out, f"plot_{i + 1}.png"))]

    res = os.path.join(d, "results")
    if os.path.isdir(res):
        shutil.copytree(res, os.path.join(out, "results"), dirs_exist_ok=True)

    dl = os.path.join(SITE, "downloads")
    os.makedirs(dl, exist_ok=True)
    zip_name = f"{eid}.zip"
    with zipfile.ZipFile(os.path.join(dl, zip_name), "w", zipfile.ZIP_DEFLATED) as z:
        for f in [model_path] + files + [os.path.join(d, "README.md")]:
            z.write(f, f"{eid}/{os.path.basename(f)}")
        if svg:
            z.writestr(f"{eid}/diagram.svg", svg)
        if os.path.isdir(res):
            for f in sorted(os.listdir(res)):
                z.write(os.path.join(res, f), f"{eid}/results/{f}")
    size = human(os.path.getsize(os.path.join(dl, zip_name)))
    html_ = page(meta, body, model, plugins, svg, plots, tracks[meta["track"]], files, zip_name, size)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html_)
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--run", action="store_true", help="run each model and regenerate plots")
    ap.add_argument("--columns", action="store_true", help="print output column names (with --run)")
    ap.add_argument("--console", default=os.environ.get("OHQ_CONSOLE", "OpenHydroQual-Console"))
    ap.add_argument("--resources", default=os.environ.get("OHQ_RESOURCES", ""))
    ap.add_argument("--docs", default=os.environ.get("OHQ_DOCS", ""),
                    help="folder with technical guide PDFs to publish under site/docs")
    args = ap.parse_args()
    if not args.resources:
        raise SystemExit("set --resources or OHQ_RESOURCES to the OpenHydroQual resources folder")
    if args.docs:
        os.makedirs(os.path.join(SITE, "docs"), exist_ok=True)
        for f in os.listdir(args.docs):
            if f.endswith(".pdf"):
                shutil.copy2(os.path.join(args.docs, f), os.path.join(SITE, "docs", f))
    tr = yaml.safe_load(open(TRACKS))
    tracks = {t["id"]: t for t in tr}
    ids = args.ids or sorted(x for x in os.listdir(EX) if os.path.exists(os.path.join(EX, x, "README.md")))
    metas, failed = [], []
    for eid in ids:
        print(f"• {eid}")
        m = build_one(eid, args, tracks)
        if m.get("_failed"):
            failed.append(eid)
    # catalog always covers every example, even when only some were rebuilt
    for eid in sorted(x for x in os.listdir(EX) if os.path.exists(os.path.join(EX, x, "README.md"))):
        meta, _ = read_readme(os.path.join(EX, eid, "README.md"))
        meta["id"] = eid
        meta.setdefault("status", "ready")
        entry = {k: meta[k] for k in CATALOG_FIELDS if k in meta}
        if os.path.exists(os.path.join(SITE, "examples", eid, "thumb.svg")) and entry["status"] == "ready":
            entry["thumb"] = f"examples/{eid}/thumb.svg"
        metas.append(entry)
    order = {t["id"]: i for i, t in enumerate(tr)}
    metas.sort(key=lambda m: (order.get(m["track"], 99), m.get("order", 50), m["level"], m["title"]))
    os.makedirs(os.path.join(SITE, "data"), exist_ok=True)
    tmp = os.path.join(SITE, "data", f".catalog.{os.getpid()}.json")
    json.dump({"tracks": tr, "examples": metas}, open(tmp, "w"), indent=1)
    os.replace(tmp, os.path.join(SITE, "data", "catalog.json"))
    print(f"catalog: {len(metas)} examples" + (f"; FAILED: {failed}" if failed else ""))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
