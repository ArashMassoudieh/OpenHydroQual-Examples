# Curating an example

Every example is a folder `examples/<id>/` containing:

| File | Purpose |
|---|---|
| `<name>.ohq` | The model. Exactly one, unless `model:` is set in the front matter. |
| input files | Every `.csv` / `.txt` the model reads, referenced by bare file name. |
| `README.md` | YAML front matter (catalog metadata, component descriptions, plots) + the reference documentation in Markdown. |

`tools/build.py` turns this into `site/examples/<id>/index.html`, a diagram, result plots and `site/downloads/<id>.zip`.
The reference example is `examples/reaction-network/`. Match its depth and tone.

## 1. The model file

- Template lines use bare names only: `loadtemplate; filename = main_components.json` once, then one
  `addtemplate; filename = <plugin>.json` per plugin actually used. No absolute paths, no duplicate templates.
- Give objects meaningful names (`Pond`, `Underdrain`, `Soil_layer_1`), not `Pond (1)` or `Reactor (2)`.
  When renaming, update every reference: link `from=` / `to=`, observation `object=`, sources assigned to blocks
  (e.g. `Precipitation=Storm`), and expressions.
- Write units explicitly where the GUI would (`Storage=10[m~^3]`). Prefer SI.
- Rename input files to clear names (`rainfall.csv`, `inflow.txt`, `temperature.csv`) and update references.
- System settings: keep `alloutputfile=output.txt`, start/end time, time-step settings. Drop
  GA/MCMC/observed-output file settings unless the example is about calibration.
- Tidy canvas coordinates (`x`, `y`) so the diagram reads left to right or top to bottom without overlaps.
  Blocks are usually `_width=200,_height=200`.
- Remove properties the current plugins no longer define. Check names against
  `/home/arash/Projects/OpenHydroQual/resources/<plugin>.json` (property keys and their `description`,
  `unit`, `helptext`, `expression`).
- Keep run time reasonable: well under two minutes if possible.

## 2. Running

```bash
cd /home/arash/Projects/OpenHydroQual-Examples
export OHQ_CONSOLE=/home/arash/Projects/OpenHydroQual/terminal/TOpenHydroQual/OpenHydroQual-Console
export OHQ_RESOURCES=/home/arash/Projects/OpenHydroQual/resources
OMP_NUM_THREADS=2 nice -n 15 .venv/bin/python tools/build.py --run --columns <id>
```

`--columns` prints every output series name, for choosing `plots:`. The console alone:
`$OHQ_CONSOLE model.ohq -q -r $OHQ_RESOURCES` (exit 0 = ok, 4 = model errors listed, 5 = solve failed).
Run it in a scratch copy, because it writes output files next to the model. Headless calibration
binaries: `terminal/OHQ-LM/build/OHQ-LM`, `terminal/OHQ-GA/OHQ-GA`, `terminal/OHQ-MCMC/OHQ-MCMC` in the OpenHydroQual repo.

## 3. README front matter

```yaml
title: Short Title Case Name
track: start | wq | storm | hydro | soil | hyd | mgmt | calib | auto
level: 1 | 2 | 3            # beginner, intermediate, advanced
status: ready               # 'planned' until the model runs and the doc is complete
summary: One or two sentences for the catalog card.
plugins: [plugin file names without .json, excluding main_components unless nothing else]
features: [3-5 short capability tags]
keywords: [10-20 search terms: processes, synonyms, acronyms, application areas]
doc: optional_pdf_in_site_docs.pdf
extra_files: [optional additional files for the zip, e.g. other .ohq variants]
components:                 # keyed by object name (or by type, for many identical objects)
  ObjectName: What it physically represents in this model, and the role it plays.
inputs:
  file.csv: What the series is, units of both columns, source if real data.
plots:
  - title: Plot title
    ylabel: Label (units)
    series:
      - {column: "Block_Name_property", label: "Legend text"}
    caption: One sentence on what the plot shows.
```

Plot series can also come from a file in the example folder, to overlay an analytical solution or
observed data: `{file: "exact_solution.csv", label: "Analytical", style: points}` (two numeric columns,
non-numeric header lines skipped). `style` is `line` (default), `dashed` or `points`; `color` is optional, and `scale` multiplies values (unit conversion, e.g. `scale: 1.157e-5` for m³/day to m³/s).
Per plot (or per series): `linewidth: 0.6` thins lines so fast cycles stay visible. Per plot: `xlim: [a, b]`, `ylim: [a, b]`, `logy: true`, and `hlines: [{y: 4.0e6, label: "S_min"}]` for reference levels. A series `{columns: [a, b, c], label: "Total outflow"}` plots the sum of several outputs.

Figures that the forward run cannot produce (calibration fits, posterior histograms) go in a
`results/` subfolder. The build copies it to the site and into the zip. Reference such figures from the README body as
`![Caption](results/fit.png)`.

Quote YAML values that contain `: `. Every block, link, source, constituent, reaction and parameter
should have a `components` entry, except long runs of identical objects (for example 30 soil cells).
For those, key the entry by the type name.

## 4. README body (the documentation)

Sections, in this order:

1. `## What this model represents`: the physical system and why someone would build it.
2. `## How it works`: governing relationships, taken from the plugin JSON `expression` fields, written as equations,
   how the components connect, and how the inputs drive the model.
3. `## What to look for in the results`: concrete observations, tied to the plots.
4. `## Assumptions and limitations`.

Rules:
- This is reference documentation, not a click-by-click tutorial. No GUI steps.
- Describe only what the model actually contains. Verify every equation against the plugin JSON. Do not guess.
- Plain, precise language. No em dashes (use commas, colons, parentheses). Never use the phrase "rather than".
- Metric units; state units for every number.
- Sign conventions: say which direction is positive for links that can reverse.

## 5. Done means

- `build.py --run <id>` exits 0 with no `!` warnings, and the plots show physically sensible behavior.
- `status: ready` is set.
- The original source model in Aquifolium or the OpenHydroQual repo is untouched. Work on copies inside `examples/<id>/`.
