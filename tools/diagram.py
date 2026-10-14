"""Render an OpenHydroQual model canvas to SVG from block positions in the .ohq."""
import base64
import html
import math
import os
import re

from PIL import Image

ICON_PX = 96


def make_icon(resources, filename, out_dir):
    """Downscale a plugin icon into out_dir; return the file name or None."""
    if not filename:
        return None
    src = os.path.join(resources, "Icons", filename)
    if not os.path.exists(src):
        return None
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(filename)[0] + ".png"
    dst = os.path.join(out_dir, base)
    if not os.path.exists(dst):
        im = Image.open(src).convert("RGBA")
        im.thumbnail((ICON_PX, ICON_PX), Image.LANCZOS)
        im.save(dst, optimize=True)
    return base


def _box(o):
    p = o["props"]
    try:
        x, y = float(p.get("x", 0)), float(p.get("y", 0))
        w, h = float(p.get("_width", 200)), float(p.get("_height", 200))
    except ValueError:
        return None
    return x, y, w, h


def _clip(cx, cy, w, h, tx, ty):
    """Point where the ray from box center toward (tx,ty) leaves the box."""
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (w / 2) / abs(dx) if dx else math.inf
    sy = (h / 2) / abs(dy) if dy else math.inf
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def render(model, plugins, resources, icon_dir, icon_href="icons/"):
    """Return (svg_text, n_drawn). Icons are written to icon_dir."""
    nodes = {}
    for o in model.of_kind("block", "composite"):
        b = _box(o)
        if b:
            nodes[o["name"]] = (o, b)
    if not nodes:
        return None, 0

    def find(name):
        if name in nodes:
            return nodes[name]
        # links into composite members are named "<composite>..." in the expanded model
        for n in sorted(nodes, key=len, reverse=True):
            if name.startswith(n):
                return nodes[n]
        return None

    pad, label_h = 60, 46
    xs = [b[0] for _, b in nodes.values()] + [b[0] + b[2] for _, b in nodes.values()]
    ys = [b[1] for _, b in nodes.values()] + [b[1] + b[3] + label_h for _, b in nodes.values()]
    minx, maxx, miny, maxy = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    W, H = maxx - minx, maxy - miny
    font = max(14, min(W, H) / 45, W / 70)

    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx:.0f} {miny:.0f} {W:.0f} {H:.0f}" '
             f'class="ohq-diagram" style="max-width:{W * 0.5:.0f}px" role="img" aria-label="Model diagram">',
             '<defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" '
             'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="d-arrow"/></marker></defs>']

    drawn_pairs = {}
    for o in model.of_kind("link"):
        a, b = find(o["props"].get("from", "")), find(o["props"].get("to", ""))
        if not a or not b or a is b:
            continue
        (_, (ax, ay, aw, ah)), (_, (bx, by, bw, bh)) = a, b
        acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
        key = tuple(sorted([a[0]["name"], b[0]["name"]]))
        k = drawn_pairs.get(key, 0)
        drawn_pairs[key] = k + 1
        # offset parallel links between the same pair
        nx, ny = -(bcy - acy), (bcx - acx)
        nl = math.hypot(nx, ny) or 1
        off = (k - 0) * 18 * (1 if k % 2 else -1) if k else 0
        ox, oy = nx / nl * off, ny / nl * off
        x1, y1 = _clip(acx, acy, aw, ah, bcx, bcy)
        x2, y2 = _clip(bcx, bcy, bw, bh, acx, acy)
        mx, my = (x1 + x2) / 2 + ox, (y1 + y2) / 2 + oy
        title = html.escape(f'{o["name"]} ({o["type"]})')
        parts.append(f'<g class="d-link" data-name="{html.escape(o["name"])}"><title>{title}</title>'
                     f'<path d="M{x1+ox:.1f} {y1+oy:.1f} L{mx:.1f} {my:.1f} L{x2+ox:.1f} {y2+oy:.1f}" '
                     f'marker-mid="url(#arr)"/></g>')

    for name, (o, (x, y, w, h)) in nodes.items():
        ic = make_icon(resources, plugins.icon(o["type"]), icon_dir)
        title = html.escape(f'{name} ({o["type"]})')
        cls = "d-node composite" if o["kind"] == "composite" else "d-node"
        parts.append(f'<g class="{cls}" data-name="{html.escape(name)}"><title>{title}</title>'
                     f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{min(w,h)*0.08:.0f}"/>')
        if ic:
            s = min(w, h) * 0.78
            parts.append(f'<image href="{icon_href}{ic}" x="{x + (w - s) / 2:.0f}" y="{y + (h - s) / 2:.0f}" '
                         f'width="{s:.0f}" height="{s:.0f}"/>')
        parts.append(f'<text x="{x + w / 2:.0f}" y="{y + h + font * 1.3:.0f}" font-size="{font:.0f}" '
                     f'text-anchor="middle">{html.escape(name)}</text></g>')
    parts.append("</svg>")
    return "\n".join(parts), len(nodes)


def thumbnail(svg, icon_dir):
    """Self-contained copy of a diagram for use in <img>: icons embedded once as data URIs,
    labels and link titles dropped, fixed light styling."""
    ids = {}

    def defs_for(m):
        fn = m.group(1)
        if fn not in ids:
            ids[fn] = f"i{len(ids)}"
        return f'<use href="#{ids[fn]}" x="{m.group(2)}" y="{m.group(3)}" width="{m.group(4)}" height="{m.group(5)}"/>'

    body = re.sub(r'<image href="icons/([^"]+)" x="([^"]+)" y="([^"]+)" width="([^"]+)" height="([^"]+)"/>', defs_for, svg)
    body = re.sub(r"<text[^>]*>.*?</text>", "", body)
    body = re.sub(r"<title>.*?</title>", "", body)
    body = re.sub(r' style="max-width:[^"]*"', "", body)
    sym = []
    for fn, i in ids.items():
        data = base64.b64encode(open(os.path.join(icon_dir, fn), "rb").read()).decode()
        sym.append(f'<symbol id="{i}" viewBox="0 0 1 1"><image href="data:image/png;base64,{data}" '
                   f'width="1" height="1" preserveAspectRatio="xMidYMid meet"/></symbol>')
    style = ("<style>.d-node rect{fill:#fff;stroke:#c9d3df;stroke-width:3}"
             ".d-node.composite rect{stroke-dasharray:10 6}"
             ".d-link path{stroke:#5b7a99;stroke-width:5;fill:none}.d-arrow{fill:#5b7a99}</style>")
    return body.replace("<defs>", "<defs>" + style + "".join(sym), 1)
