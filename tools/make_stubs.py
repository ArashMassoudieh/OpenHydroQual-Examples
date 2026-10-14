#!/usr/bin/env python3
"""Create examples/<id>/README.md stubs (status: planned) from tools/seed.yaml."""
import os
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for e in yaml.safe_load(open(os.path.join(ROOT, "tools", "seed.yaml"))):
    d = os.path.join(ROOT, "examples", e["id"])
    p = os.path.join(d, "README.md")
    if os.path.exists(p):
        continue
    os.makedirs(d, exist_ok=True)
    meta = {k: v for k, v in e.items() if k != "id"}
    meta["status"] = "planned"
    with open(p, "w") as f:
        f.write("---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True) + "---\n")
    print("stub", e["id"])
