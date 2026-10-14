# OpenHydroQual Examples

Source for the searchable examples catalog linked from [openhydroqual.com](https://openhydroqual.com).
Each example is a ready-to-run OpenHydroQual model with its input data and reference documentation
explaining what the model represents and what every component does.

## Layout

```
examples/<id>/          one folder per example: model (.ohq), input files, README.md
tools/build.py          generates the site from examples/
tools/ohqlib.py         .ohq and plugin JSON reader
tools/diagram.py        renders model diagrams from canvas positions
tools/seed.yaml         original catalog plan (used once to create stubs)
tracks.yaml             catalog tracks (categories) and colors
site/                   the published static site (GitHub Pages)
CURATION.md             how to add or update an example
```

## Building locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
export OHQ_RESOURCES=/path/to/OpenHydroQual/resources
export OHQ_CONSOLE=/path/to/OpenHydroQual-Console
export OHQ_DOCS=/path/to/OpenHydroQual/docs
.venv/bin/python tools/build.py --run            # all examples, re-running every model
.venv/bin/python tools/build.py --run <id>       # one example
python3 -m http.server -d site 8000              # preview at http://localhost:8000
```

Without `--run`, the build reuses the committed result plots. The GitHub Actions workflow builds
without `--run` and deploys `site/` to GitHub Pages on every push to `main`.

## Adding an example

See [CURATION.md](CURATION.md).
