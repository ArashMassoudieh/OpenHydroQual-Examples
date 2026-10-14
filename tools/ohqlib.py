"""Read OpenHydroQual .ohq scripts and plugin (template) JSON files.

Used by build.py to generate model diagrams and component reference tables.
"""
import html
import json
import os
import re

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "theta": "θ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ",
    "phi": "φ", "omega": "ω", "Delta": "Δ", "Omega": "Ω", "Theta": "Θ", "kappa": "κ", "eta": "η",
}

# Properties that only describe GUI layout or identity.
LAYOUT_KEYS = {"x", "y", "_width", "_height", "name", "type", "from", "to", "object"}


def split_top(s, sep=","):
    """Split on sep, ignoring separators inside (), [] or {}."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return [p for p in out if p.strip() != ""]


def split_value_unit(v):
    m = re.match(r"^(.*?)\[([^\[\]]*)\]$", v.strip())
    if m and m.group(1) != "":
        return m.group(1), m.group(2)
    return v, ""


def pretty_unit(u):
    """Render OHQ unit/markup (m~^3, ~alpha) as HTML."""
    if not u:
        return ""
    u = html.escape(u)
    u = re.sub(r"~\^(-?[0-9.]+)", r"<sup>\1</sup>", u)
    u = re.sub(r"~_([A-Za-z0-9]+)", r"<sub>\1</sub>", u)
    u = re.sub(r"~([A-Za-z]+)", lambda m: GREEK.get(m.group(1), m.group(1)), u)
    return u


def pretty_text(t):
    return pretty_unit(t) if t else ""


class Model:
    def __init__(self, path):
        self.path = path
        self.templates = []
        self.objects = []          # dicts: kind, type, name, props
        self.system = {}
        self.estimated = []        # setasparameter entries
        self._parse(open(path, encoding="utf-8", errors="replace").read())

    def _parse(self, text):
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            head, _, rest = line.partition(";")
            head = head.strip()
            low = head.lower()
            if low in ("loadtemplate", "addtemplate"):
                m = re.search(r"filename\s*=\s*(.+)$", rest)
                if m:
                    t = os.path.basename(m.group(1).strip())
                    if t not in self.templates:
                        self.templates.append(t)
            elif low.startswith("create "):
                kind = head.split(None, 1)[1].strip()
                props = {}
                for part in split_top(rest):
                    k, _, v = part.partition("=")
                    props[k.strip()] = v.strip()
                self.objects.append({"kind": kind, "type": props.get("type", ""),
                                     "name": props.get("name", ""), "props": props})
            elif low == "setvalue":
                props = dict((k.strip(), v.strip()) for k, _, v in
                             (p.partition("=") for p in split_top(rest)))
                if props.get("object") == "system":
                    self.system[props.get("quantity")] = props.get("value", "")
            elif low == "setasparameter":
                props = dict((k.strip(), v.strip()) for k, _, v in
                             (p.partition("=") for p in split_top(rest)))
                self.estimated.append(props)

    def of_kind(self, *kinds):
        return [o for o in self.objects if o["kind"] in kinds]

    def data_files(self):
        """Bare file names of .txt/.csv inputs referenced by object properties."""
        files = []
        for o in self.objects:
            for k, v in o["props"].items():
                v = re.sub(r"\s*\[[^\]]*\]$", "", v)  # strip trailing [unit]
                if re.search(r"\.(csv|txt)$", v, re.I) and k not in ("name",):
                    f = os.path.basename(v.replace("\\", "/"))
                    if f not in files:
                        files.append(f)
        return files


class Plugins:
    def __init__(self, resources, templates):
        self.types = {}
        self.source = {}
        names = ["main_components.json"] + [t for t in templates if t != "main_components.json"]
        for t in names:
            p = os.path.join(resources, t)
            if not os.path.exists(p):
                continue
            d = json.load(open(p, encoding="utf-8"))
            for k, v in d.items():
                if isinstance(v, dict) and "type" in v:
                    self.types[k] = v
                    self.source[k] = t.replace(".json", "")

    def get(self, typename):
        return self.types.get(typename, {})

    def icon(self, typename):
        ic = self.get(typename).get("icon")
        return ic.get("filename") if isinstance(ic, dict) else None

    def describe(self, typename):
        d = self.get(typename)
        return (d.get("helptext") or d.get("description") or "").strip()

    def prop_info(self, typename, prop, qualifier_type=None):
        """(label, unit, meaning) for a property of a type.

        'A:concentration' style properties are looked up on the constituent's type
        (qualifier_type). When a property has no helptext, its defining expression
        is reported instead.
        """
        key = prop.split(":")[-1] if ":" in prop else prop
        p = None
        for t in ([qualifier_type] if qualifier_type else []) + [typename]:
            cand = self.get(t).get(key)
            if isinstance(cand, dict):
                p = cand
                break
        if p is None:
            return key, "", ""
        label = (p.get("description") or key).split(";")[0]
        unit = (p.get("unit") or "").split(";")[0]
        meaning = (p.get("helptext") or "").strip()
        if not meaning and p.get("expression"):
            meaning = "Computed as " + p["expression"]
        return label, unit, meaning
