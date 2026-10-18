"""ui-mockup: turn a Roblox UI JSON spec into PNG mockups plus a layout report.

Usage:
    python mockup.py SPEC.json [--project DIR] [--style STYLE.json]

Writes <project>/mockups/NAME/NAME_<W>x<H>.png for each screen size and NAME_report.txt.
Exit codes: 0 = no failures, 1 = layout failures, 2 = the spec or style can't be used (nothing written).
"""

import argparse
import html
import json
import math
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

# ---- Rules: change the numbers here, then update SKILL.md and design.md to match ----
REF_W, REF_H = 1280, 720          # sizes and offsets in the spec are pixels at this size
SCREENS = [(640, 360), (896, 414), (1024, 768), (1280, 720), (1920, 1080)]
TOUCH_MIN = 88                    # button minimum, reference pixels
GAP_MIN = 8                       # sibling gap, reference pixels (warning only)
CORNER_CLEAR = 24                 # corner button (close, back) to every sibling, reference pixels
CENTRE_TOLERANCE = 1.5            # pixels on screen

TYPES = {"panel", "button", "label"}
TEXT_TYPES = {"button", "label"}
FIELDS = {"id", "type", "parent", "x", "y", "ox", "oy", "anchor", "w", "h",
          "text", "textSize", "textAlign", "colour", "centre", "overhang"}
TEXT_ALIGNS = {"left": "flex-start", "centre": "center", "right": "flex-end"}  # like Roblox TextXAlignment
STYLE_COLOURS = {"background", "panel", "button", "text", "outline", "shadow"}
NAME_PATTERN = re.compile(r"[A-Za-z0-9_-]+")
HEX_COLOUR = re.compile(r"#[0-9a-fA-F]{6}")
EPS = 1e-6
TEXT_EPS = 0.01


class InputError(Exception):
    """The spec or style can't be used; carries a list of plain-English problems."""


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def read_json(path, what):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise InputError([f"{what} not found: {path}"])
    except json.JSONDecodeError as err:
        raise InputError([f"{what} is not valid JSON: {err}"])


def load_style(path):
    style = read_json(path, "style file")
    errors = []
    if not isinstance(style, dict):
        raise InputError(["style file must be an object"])
    for key in ("stroke", "cornerRadius", "depth", "textSize"):
        if not is_number(style.get(key)) or style[key] < 0:
            errors.append(f"style '{key}' must be a number, 0 or more")
    if not isinstance(style.get("font"), str):
        errors.append("style 'font' must be a CSS font list, e.g. \"Arial, sans-serif\"")
    colours = style.get("colours")
    if not isinstance(colours, dict):
        errors.append("style 'colours' must be an object")
    else:
        for key in sorted(STYLE_COLOURS):
            if not isinstance(colours.get(key), str) or not HEX_COLOUR.fullmatch(colours[key]):
                errors.append(f"style colour '{key}' must look like #12ab34")
    if errors:
        raise InputError(errors)
    return style


def load_spec(path, default_text_size):
    """Read and validate SPEC.json. Returns (name, elements) or raises InputError."""
    raw = read_json(path, "spec")
    if not isinstance(raw, dict):
        raise InputError(["the top level must be an object with 'name' and 'elements'"])
    errors = []
    name = raw.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        errors.append("'name' must be letters, digits, _ or - only (it becomes the file name)")
    items = raw.get("elements")
    if not isinstance(items, list) or not items:
        raise InputError(errors + ["the spec is empty: 'elements' must list at least one element"])

    elements = {}
    for index, item in enumerate(items):
        where = f"elements[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where} must be an object")
            continue
        eid = item.get("id")
        if not isinstance(eid, str) or not eid:
            errors.append(f"{where}: 'id' must be a non-empty string")
            continue
        where = f"element '{eid}'"
        if eid in elements:
            errors.append(f"{where}: id is used twice")
            continue
        unknown = sorted(set(item) - FIELDS)
        if unknown:
            errors.append(f"{where}: unknown field(s) {', '.join(unknown)} (a typo would silently skip a check)")
        etype = item.get("type")
        if etype not in TYPES:
            errors.append(f"{where}: 'type' must be one of {', '.join(sorted(TYPES))}")
        for key in ("x", "y", "ox", "oy"):
            if not is_number(item.get(key, 0)):
                errors.append(f"{where}: '{key}' must be a number")
        for key in ("w", "h"):
            if not is_number(item.get(key)) or item[key] <= 0:
                errors.append(f"{where}: '{key}' must be a number above 0 (pixels at 1280x720)")
        anchor = item.get("anchor", [0, 0])
        if not (isinstance(anchor, list) and len(anchor) == 2 and all(is_number(n) for n in anchor)):
            errors.append(f"{where}: 'anchor' must be [x, y], e.g. [0.5, 0.5]")
        parent = item.get("parent")
        if parent is not None and not isinstance(parent, str):
            errors.append(f"{where}: 'parent' must be another element's id")
        text = item.get("text")
        if text is not None:
            if not isinstance(text, str):
                errors.append(f"{where}: 'text' must be a string")
            elif etype not in TEXT_TYPES:
                errors.append(f"{where}: only button and label can have 'text'")
        text_size = item.get("textSize", default_text_size)
        if not is_number(text_size) or text_size <= 0:
            errors.append(f"{where}: 'textSize' must be a number above 0")
        text_align = item.get("textAlign", "centre")
        if text_align not in TEXT_ALIGNS:
            errors.append(f"{where}: 'textAlign' must be \"left\", \"centre\" or \"right\"")
        elif "textAlign" in item and etype not in TEXT_TYPES:
            errors.append(f"{where}: only button and label can have 'textAlign'")
        colour = item.get("colour")
        if colour is not None and not (isinstance(colour, str) and HEX_COLOUR.fullmatch(colour)):
            errors.append(f"{where}: 'colour' must look like #12ab34")
        centre = item.get("centre", False)
        if centre not in (True, False, "x", "y"):
            errors.append(f"{where}: 'centre' must be true, \"x\" or \"y\"")
        overhang = item.get("overhang", False)
        if not isinstance(overhang, bool):
            errors.append(f"{where}: 'overhang' must be true or false")

        elements[eid] = {
            "id": eid, "type": etype, "parent": parent,
            "x": item.get("x", 0), "y": item.get("y", 0), "ox": item.get("ox", 0), "oy": item.get("oy", 0),
            "anchor": anchor, "w": item.get("w"), "h": item.get("h"),
            "text": text, "textSize": text_size, "textAlign": text_align, "colour": colour,
            "centre": centre, "overhang": overhang,
        }

    for el in elements.values():
        if el["parent"] is not None and el["parent"] not in elements:
            errors.append(f"element '{el['id']}': parent '{el['parent']}' doesn't exist")
    if not errors:
        for el in elements.values():
            seen, current = set(), el
            while current["parent"] is not None:
                if current["id"] in seen:
                    errors.append(f"element '{el['id']}': its parent chain loops back on itself")
                    break
                seen.add(current["id"])
                current = elements[current["parent"]]
    if errors:
        raise InputError(errors)
    return name, list(elements.values())


def layout(elements, width, height):
    """Screen rectangle (left, top, right, bottom) of every element, plus the page scale."""
    scale = min(width / REF_W, height / REF_H)
    by_id = {el["id"]: el for el in elements}
    rects = {}

    def rect_of(eid):
        if eid is None:
            return (0.0, 0.0, float(width), float(height))
        if eid not in rects:
            el = by_id[eid]
            pl, pt, pr, pb = rect_of(el["parent"])
            w, h = el["w"] * scale, el["h"] * scale
            left = pl + (pr - pl) * el["x"] + el["ox"] * scale - el["anchor"][0] * w
            top = pt + (pb - pt) * el["y"] + el["oy"] * scale - el["anchor"][1] * h
            rects[eid] = (left, top, left + w, top + h)
        return rects[eid]

    for el in elements:
        rect_of(el["id"])
    return rects, scale


def fmt(value):
    return str(round(value)) if abs(value - round(value)) < 0.05 else f"{value:.1f}"


def sticking_out(inner, outer):
    """How far inner pokes past outer on each side, e.g. ['right by 20px']."""
    sides = [("left", outer[0] - inner[0]), ("top", outer[1] - inner[1]),
             ("right", inner[2] - outer[2]), ("bottom", inner[3] - outer[3])]
    return [f"{side} by {fmt(amount)}px" for side, amount in sides if amount > EPS]


def is_corner_button(el):
    """A button pinned to a corner of its parent, like a close or back button."""
    return (el["type"] == "button" and el["parent"] is not None
            and all(el["anchor"][i] in (0, 1) and el["xy"[i]] == el["anchor"][i] for i in (0, 1)))


def check_geometry(elements, rects, scale, width, height):
    """Every check except text_fit. Returns {element id: [(status, check, detail), ...]}."""
    rows = {el["id"]: [] for el in elements}
    order = {el["id"]: i for i, el in enumerate(elements)}
    screen = (0, 0, width, height)
    gap_min = GAP_MIN * scale

    for el in elements:
        eid, rect = el["id"], rects[el["id"]]
        add = lambda status, check, detail: rows[eid].append((status, check, detail))
        w_px, h_px = rect[2] - rect[0], rect[3] - rect[1]

        if el["type"] == "button":
            ok = el["w"] >= TOUCH_MIN and el["h"] >= TOUCH_MIN
            add("PASS" if ok else "FAIL", "touch_target",
                f"{eid} {fmt(el['w'])}x{fmt(el['h'])} at 1280x720 ({fmt(w_px)}x{fmt(h_px)}px here), "
                f"min {TOUCH_MIN}x{TOUCH_MIN}")

        siblings = [o for o in elements if o["parent"] == el["parent"] and o is not el]
        if siblings:
            any_overlap = any_close = False
            nearest = None
            for other in siblings:
                o = rects[other["id"]]
                first = order[eid] < order[other["id"]]  # report each pair once
                dx = max(o[0] - rect[2], rect[0] - o[2])
                dy = max(o[1] - rect[3], rect[1] - o[3])
                if dx < -EPS and dy < -EPS:
                    any_overlap = True
                    if first:
                        ow = min(rect[2], o[2]) - max(rect[0], o[0])
                        oh = min(rect[3], o[3]) - max(rect[1], o[1])
                        detail = f"{eid} overlaps {other['id']} by {fmt(ow)}x{fmt(oh)}px"
                        if el["overhang"] or other["overhang"]:
                            add("PASS", "overlap", detail + " (allowed: overhang)")
                        else:
                            add("FAIL", "overlap", detail)
                    continue
                gap = max(dx, dy)
                if nearest is None or gap < nearest[1]:
                    nearest = (other["id"], gap)
                if gap < gap_min - EPS:
                    any_close = True
                    if first:
                        add("WARN", "gap", f"{eid} to {other['id']} gap {fmt(gap)}px, "
                                           f"min {fmt(gap_min)}px here ({GAP_MIN} at 1280x720)")
            if not any_overlap:
                add("PASS", "overlap", f"{eid} overlaps no siblings")
            if nearest and not any_close:
                add("PASS", "gap", f"{eid} nearest sibling {nearest[0]} gap {fmt(nearest[1])}px, "
                                   f"min {fmt(gap_min)}px here")
            if is_corner_button(el):
                corner_min = CORNER_CLEAR * scale
                ok = not any_overlap and nearest[1] >= corner_min - EPS
                closest = "overlaps a sibling" if any_overlap else f"nearest sibling {nearest[0]} gap {fmt(nearest[1])}px"
                add("PASS" if ok else "FAIL", "corner_clear",
                    f"{eid} is a corner button, {closest}, min {fmt(corner_min)}px here ({CORNER_CLEAR} at 1280x720)")

        if el["centre"]:
            parent = rects[el["parent"]] if el["parent"] else screen
            axes = "xy" if el["centre"] is True else el["centre"]
            parts, hints, ok = [], [], True
            for axis in axes:
                i = 0 if axis == "x" else 1
                off = abs((rect[i] + rect[i + 2]) / 2 - (parent[i] + parent[i + 2]) / 2)
                parts.append(f"{axis} {fmt(off)}px")
                if off > CENTRE_TOLERANCE + EPS:
                    ok = False
                    if el[axis] == 0.5 and el["anchor"][i] != 0.5:
                        hints.append(f"{axis} is 0.5 but anchor {axis} is {fmt(el['anchor'][i])}, "
                                     f"so it isn't centred: set anchor {axis} to 0.5")
            detail = f"{eid} off centre by {', '.join(parts)} (max {CENTRE_TOLERANCE})"
            add("PASS" if ok else "FAIL", "off_centre", "; ".join([detail] + hints))

        if el["parent"]:
            out = sticking_out(rect, rects[el["parent"]])
            if not out:
                add("PASS", "outside_parent", f"{eid} inside {el['parent']}")
            elif el["overhang"]:
                add("PASS", "outside_parent", f"{eid} sticks out of {el['parent']} {', '.join(out)} (allowed: overhang)")
            else:
                add("FAIL", "outside_parent", f"{eid} sticks out of {el['parent']} {', '.join(out)}")

        out = sticking_out(rect, screen)
        add("FAIL" if out else "PASS", "off_screen",
            f"{eid} sticks out of the {width}x{height} screen {', '.join(out)}" if out else f"{eid} inside screen")
    return rows


def lighter(colour, amount=0.3):
    """Mix a #rrggbb colour with white, for the top of the button gradient."""
    rgb = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(c + (255 - c) * amount):02x}" for c in rgb)


def darker(colour, amount=0.5):
    """Mix a #rrggbb colour with black, for the shadow under a recoloured button."""
    rgb = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(c * (1 - amount)):02x}" for c in rgb)


def element_style(el, depth):
    """Inline CSS for this element's own textAlign and colour."""
    css = []
    if el["textAlign"] != "centre":
        css.append(f"justify-content:{TEXT_ALIGNS[el['textAlign']]}")
    colour = el["colour"]
    if colour and el["type"] == "panel":
        css.append(f"background:{colour}")
    elif colour and el["type"] == "button":
        css.append(f"background:linear-gradient(to bottom,{lighter(colour)},{colour});"
                   f"box-shadow:0 {depth}px 0 {darker(colour)}")
    return ";".join(css)


def build_html(elements, rects, scale, width, height, style):
    c = style["colours"]
    stroke, radius, depth = (style[k] * scale for k in ("stroke", "cornerRadius", "depth"))
    css = f"""
html, body {{ margin: 0; width: {width}px; height: {height}px; overflow: hidden; background: {c['background']}; }}
.el {{ position: absolute; box-sizing: border-box; display: flex; align-items: center; justify-content: center; }}
.el span {{ white-space: pre; flex-shrink: 0; line-height: 1.2; font-family: {style['font']}; font-weight: 700; color: {c['text']}; }}
.panel {{ background: {c['panel']}; border: {stroke}px solid {c['outline']}; border-radius: {radius}px; }}
.button {{ background: linear-gradient(to bottom, {lighter(c['button'])}, {c['button']});
          border: {stroke}px solid {c['outline']}; border-radius: {radius}px; box-shadow: 0 {depth}px 0 {c['shadow']}; }}
.fail {{ outline: 3px solid #ff3c3c; }}
"""
    children = {}
    for el in elements:
        children.setdefault(el["parent"], []).append(el)
    parts = []

    def walk(parent_id):  # parents first, so children draw on top
        for el in children.get(parent_id, []):
            left, top, right, bottom = rects[el["id"]]
            text = ""
            if el["text"]:
                text_colour = f";color:{el['colour']}" if el["colour"] and el["type"] == "label" else ""
                text = (f'<span style="font-size:{el["textSize"] * scale}px{text_colour}">'
                        f'{html.escape(el["text"])}</span>')
            own = element_style(el, depth)
            parts.append(
                f'<div class="el {el["type"]}" data-id="{html.escape(el["id"])}"{" data-text" if text else ""} '
                f'style="left:{left}px;top:{top}px;width:{right - left}px;height:{bottom - top}px'
                f'{";" + own if own else ""}">{text}</div>')
            walk(el["id"])

    walk(None)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{''.join(parts)}</body></html>"


MEASURE_TEXT = """() => Array.from(document.querySelectorAll('.el[data-text]')).map(el => {
  const text = el.querySelector('span').getBoundingClientRect();
  const box = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  const bx = parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth);
  const by = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth);
  return {id: el.dataset.id, tw: text.width, th: text.height, bw: box.width - bx, bh: box.height - by};
})"""

MARK_FAILED = """ids => ids.forEach(id =>
  document.querySelector(`[data-id="${CSS.escape(id)}"]`).classList.add('fail'))"""


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Render a Roblox UI spec at five screen sizes and check its layout.")
    parser.add_argument("spec", help="path to SPEC.json")
    parser.add_argument("--project", default=".", help="project folder; outputs go in <project>/mockups/NAME/")
    parser.add_argument("--style", default=str(SKILL_DIR / "styles" / "default.json"), help="style JSON file")
    args = parser.parse_args(argv)

    try:
        style = load_style(args.style)
        name, elements = load_spec(args.spec, style["textSize"])
    except InputError as err:
        print("ERROR: fix these and run again. Nothing was written.", file=sys.stderr)
        for message in err.args[0]:
            print(f"  - {message}", file=sys.stderr)
        return 2

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: Playwright is missing. Install it with:\n"
              "  python -m pip install --user playwright\n  python -m playwright install chromium", file=sys.stderr)
        return 2

    out_dir = Path(args.project) / "mockups" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, height in SCREENS:
            rects, scale = layout(elements, width, height)
            rows = check_geometry(elements, rects, scale, width, height)

            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.set_content(build_html(elements, rects, scale, width, height, style))
            page.evaluate("document.fonts.ready")
            for m in page.evaluate(MEASURE_TEXT):
                ok = m["tw"] <= m["bw"] + TEXT_EPS and m["th"] <= m["bh"] + TEXT_EPS
                rows[m["id"]].append(("PASS" if ok else "FAIL", "text_fit",
                                      f"{m['id']} text {fmt(m['tw'])}x{fmt(m['th'])}px in box "
                                      f"{fmt(m['bw'])}x{fmt(m['bh'])}px"))
            failed = [eid for eid, element_rows in rows.items() if any(r[0] == "FAIL" for r in element_rows)]
            page.evaluate(MARK_FAILED, failed)
            page.screenshot(path=str(out_dir / f"{name}_{width}x{height}.png"))
            page.close()

            for el in elements:
                lines += [f"{f'{width}x{height}':<11}{status}  {check:<16}{detail}"
                          for status, check, detail in rows[el["id"]]]
        browser.close()

    failures = sum(1 for line in lines if line[11:15] == "FAIL")
    warnings = sum(1 for line in lines if line[11:15] == "WARN")
    report = [f"{name} layout report"] + lines + [f"WARNINGS: {warnings}", f"RESULT: {failures} failures"]
    (out_dir / f"{name}_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    print(f"\nFiles written to {out_dir.resolve()}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
