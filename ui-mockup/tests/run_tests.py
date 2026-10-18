"""Runs ui-mockup on every test spec and checks each result is the right one.

  good/*.json  must pass: exit 0, RESULT: 0 failures, all five PNGs written.
  bad/*.json   must fail on ITS check and no other (or be refused with ITS error).
  Edge cases   sit either side of each limit, to prove the limits are exactly where the rules say.

Finding no spec files is itself a failure: a test run that checked nothing proves nothing.

Run: python tests/run_tests.py    (exit 0 = all tests passed)
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "mockup.py"
SIZES = ["640x360", "896x414", "1024x768", "1280x720", "1920x1080"]
REPORT_LINE = re.compile(r"^(\d+x\d+)\s+(PASS|FAIL|WARN)\s+(\S+)\s+(.*)$")

# bad file -> (what should happen, the check or error it must name, extra text that must appear)
EXPECTED_BAD = {
    "small_button.json": ("fail", "touch_target", None),
    "overlap.json": ("fail", "overlap", None),
    "half_anchor.json": ("fail", "off_centre", "x is 0.5 but anchor x is 0"),
    "outside.json": ("fail", "outside_parent", None),
    "offscreen.json": ("fail", "off_screen", None),
    "long_text.json": ("fail", "text_fit", None),
    "cramped_corner.json": ("fail", "corner_clear", None),
    "empty.json": ("error", "the spec is empty", None),
    "bad_parent.json": ("error", "parent 'Ghost' doesn't exist", None),
}

table = []  # (result, test, expected, got)


def record(ok, test, expected, got):
    table.append(("PASS" if ok else "FAIL", test, expected, got))


def run(spec_path, project):
    result = subprocess.run([sys.executable, str(SCRIPT), str(spec_path), "--project", str(project)],
                            capture_output=True, text=True, encoding="utf-8")
    rows = [m.groups() for m in map(REPORT_LINE.match, result.stdout.splitlines()) if m]
    return result, rows


def spec_name(path):
    return json.loads(Path(path).read_text(encoding="utf-8")).get("name")


def failed_checks(rows):
    counts = {}
    for _, status, check, _ in rows:
        if status == "FAIL":
            counts[check] = counts.get(check, 0) + 1
    return counts


with tempfile.TemporaryDirectory() as tmp:
    # 1. Good specs.
    good_files = sorted((HERE / "good").glob("*.json"))
    if not good_files:
        record(False, "good/", "at least one spec", "found none")
    for path in good_files:
        result, rows = run(path, tmp)
        out_dir = Path(tmp) / "mockups" / str(spec_name(path))
        pngs = all((out_dir / f"{spec_name(path)}_{size}.png").exists() for size in SIZES)
        warnings = sum(1 for r in rows if r[1] == "WARN")
        last = result.stdout.strip().splitlines()[-3] if result.stdout.strip() else ""
        ok = result.returncode == 0 and "RESULT: 0 failures" in result.stdout and pngs and len(rows) > 0
        got = (f"exit {result.returncode}, {len(rows)} checks, {sum(failed_checks(rows).values())} failures, "
               f"{warnings} warnings{'' if pngs else ', PNGs missing'}")
        if result.returncode == 2:
            got = f"exit 2: {result.stderr.strip().splitlines()[-1]}"
        record(ok, f"good/{path.name}", "pass, 5 PNGs", got)

    # 2. Bad specs: each must fail on its own check only.
    bad_files = sorted((HERE / "bad").glob("*.json"))
    if not bad_files:
        record(False, "bad/", "at least one spec", "found none")
    for path in bad_files:
        test = f"bad/{path.name}"
        if path.name not in EXPECTED_BAD:
            record(False, test, "listed in EXPECTED_BAD", "no expected check listed")
            continue
        kind, target, extra = EXPECTED_BAD[path.name]
        result, rows = run(path, tmp)
        if kind == "fail":
            counts = failed_checks(rows)
            ok = (result.returncode == 1 and set(counts) == {target} and counts[target] >= 1
                  and (extra is None or extra in result.stdout))
            got = f"exit {result.returncode}, " + (", ".join(f"{c} x{n}" for c, n in sorted(counts.items())) or "no failures")
            if extra:
                got += f", {'names' if extra in result.stdout else 'MISSING'} '{extra}'"
            record(ok, test, f"{target} fails, nothing else", got)
        else:
            name = spec_name(path)
            wrote = bool(name) and (Path(tmp) / "mockups" / name).exists()
            ok = result.returncode == 2 and target in result.stderr and not wrote
            got = f"exit {result.returncode}, " + ("names it" if target in result.stderr else "doesn't name it")
            got += ", wrote files" if wrote else ", nothing written"
            record(ok, test, f"error: {target}", got)

    # 3. Edge cases at 1280x720: just inside each limit passes, just outside fails.
    def panel(eid, ox, oy, w=100, h=100, **extra):
        return {"id": eid, "type": "panel", "ox": ox, "oy": oy, "w": w, "h": h, **extra}

    box = panel("Box", 100, 100, 300, 300)

    def corner(gap):  # close button in Box's top-right corner, a tile `gap` px below it
        return [box, {"id": "X", "type": "button", "parent": "Box", "x": 1, "anchor": [1, 0], "w": 96, "h": 96},
                {"id": "T", "type": "panel", "parent": "Box", "x": 1, "oy": 96 + gap, "anchor": [1, 0], "w": 100, "h": 50}]

    edges = [
        ("gap 8px", "gap", "A", "PASS", [panel("A", 100, 100), panel("B", 208, 100)]),
        ("gap 7px", "gap", "A", "WARN", [panel("A", 100, 100), panel("B", 207, 100)]),
        ("edges touching", "overlap", "A", "PASS", [panel("A", 100, 100), panel("B", 200, 100)]),
        ("1px overlap", "overlap", "A", "FAIL", [panel("A", 100, 100), panel("B", 199, 100)]),
        ("overlap + overhang", "overlap", "A", "PASS", [panel("A", 100, 100), panel("B", 150, 100, overhang=True)]),
        ("1.5px off centre", "off_centre", "A", "PASS",
         [{"id": "A", "type": "panel", "x": 0.5, "ox": 1.5, "anchor": [0.5, 0], "w": 100, "h": 100, "centre": "x"}]),
        ("2px off centre", "off_centre", "A", "FAIL",
         [{"id": "A", "type": "panel", "x": 0.5, "ox": 2, "anchor": [0.5, 0], "w": 100, "h": 100, "centre": "x"}]),
        ("96x96 button", "touch_target", "A", "PASS", [{"id": "A", "type": "button", "ox": 100, "oy": 100, "w": 96, "h": 96}]),
        ("95x96 button", "touch_target", "A", "FAIL", [{"id": "A", "type": "button", "ox": 100, "oy": 100, "w": 95, "h": 96}]),
        ("child on parent edge", "outside_parent", "C", "PASS",
         [box, {"id": "C", "type": "panel", "parent": "Box", "x": 1, "anchor": [1, 0], "w": 50, "h": 50}]),
        ("child 1px past parent", "outside_parent", "C", "FAIL",
         [box, {"id": "C", "type": "panel", "parent": "Box", "x": 1, "ox": 1, "anchor": [1, 0], "w": 50, "h": 50}]),
        ("child past parent + overhang", "outside_parent", "C", "PASS",
         [box, {"id": "C", "type": "panel", "parent": "Box", "x": 1, "anchor": [0.5, 0.5], "w": 50, "h": 50, "overhang": True}]),
        ("corner button 24px clear", "corner_clear", "X", "PASS", corner(24)),
        ("corner button 23px clear", "corner_clear", "X", "FAIL", corner(23)),
        ("button not in a corner", "corner_clear", "X", "no line",
         [box, {"id": "X", "type": "button", "parent": "Box", "x": 0.5, "anchor": [0.5, 0], "w": 96, "h": 96},
          {"id": "T", "type": "panel", "parent": "Box", "oy": 106, "w": 50, "h": 50}]),
        ("on the screen edge", "off_screen", "A", "PASS", [{"id": "A", "type": "panel", "x": 1, "anchor": [1, 0], "w": 100, "h": 100}]),
        ("1px past the screen", "off_screen", "A", "FAIL",
         [{"id": "A", "type": "panel", "x": 1, "ox": 1, "anchor": [1, 0], "w": 100, "h": 100}]),
        ("short text, wide box", "text_fit", "A", "PASS",
         [{"id": "A", "type": "label", "ox": 100, "oy": 100, "w": 200, "h": 40, "text": "Hi", "textSize": 24}]),
        ("text taller than box", "text_fit", "A", "FAIL",
         [{"id": "A", "type": "label", "ox": 100, "oy": 100, "w": 200, "h": 20, "text": "Hi", "textSize": 24}]),
        ("typo'd field", "error", None, "unknown field(s) centred", [{"id": "A", "type": "panel", "w": 10, "h": 10, "centred": True}]),
        ("bad textAlign", "error", None, "'textAlign' must be",
         [{"id": "A", "type": "label", "w": 10, "h": 10, "text": "Hi", "textAlign": "middle"}]),
        ("textAlign on a panel", "error", None, "only button and label can have 'textAlign'",
         [{"id": "A", "type": "panel", "w": 10, "h": 10, "textAlign": "left"}]),
        ("bad colour", "error", None, "'colour' must look like", [{"id": "A", "type": "panel", "w": 10, "h": 10, "colour": "red"}]),
    ]
    for number, (label, check, element, wanted, elements) in enumerate(edges):
        path = Path(tmp) / f"Edge{number}.json"
        path.write_text(json.dumps({"name": f"Edge{number}", "elements": elements}), encoding="utf-8")
        result, rows = run(path, tmp)
        if check == "error":
            ok = result.returncode == 2 and wanted in result.stderr
            record(ok, f"edge: {label}", f"error: {wanted}", f"exit {result.returncode}")
            continue
        found = [r[1] for r in rows if r[0] == "1280x720" and r[2] == check and r[3].startswith(element + " ")]
        got = found[0] if found else "no line"
        record(got == wanted, f"edge: {label}", f"{check} {wanted}", f"{check} {got}")

    # 4. The real output: textAlign and colour only matter if they show up in the PNG, so read its pixels.
    def render_1280(name, elements):
        path = Path(tmp) / f"{name}.json"
        path.write_text(json.dumps({"name": name, "elements": elements}), encoding="utf-8")
        run(path, tmp)
        return Image.open(Path(tmp) / "mockups" / name / f"{name}_1280x720.png").convert("RGB")

    def bright_columns(image, left, top, right, bottom):
        """Leftmost and rightmost x with white text pixels inside the box."""
        xs = [x for x in range(left, right) for y in range(top, bottom) if sum(image.getpixel((x, y))) > 600]
        return (min(xs), max(xs)) if xs else None

    def label(align=None, colour=None):
        el = {"id": "A", "type": "label", "ox": 100, "oy": 100, "w": 600, "h": 60, "text": "Settings", "textSize": 40}
        if align:
            el["textAlign"] = align
        if colour:
            el["colour"] = colour
        return [el]

    for align, test, expected in [("left", lambda l, r: l < 110, "text starts within 10px of x 100"),
                                  ("right", lambda l, r: r > 690, "text ends within 10px of x 700"),
                                  (None, lambda l, r: l > 250 and r < 550, "text in the middle of 100-700")]:
        span = bright_columns(render_1280(f"Align{align}", label(align)), 100, 100, 700, 160)
        got = f"text spans x {span[0]}-{span[1]}" if span else "no text found"
        record(bool(span) and test(*span), f"render: textAlign {align or 'default (centre)'}", expected, got)

    pixel = render_1280("ColourPanel", [{"id": "A", "type": "panel", "ox": 100, "oy": 100, "w": 200, "h": 100,
                                         "colour": "#ff0000"}]).getpixel((200, 150))
    record(pixel == (255, 0, 0), "render: panel colour", "pixel (255, 0, 0)", f"pixel {pixel}")

    image = render_1280("ColourButton", [{"id": "A", "type": "button", "ox": 100, "oy": 100, "w": 200, "h": 100,
                                          "colour": "#808080"}])
    top, bottom, shadow = image.getpixel((200, 105)), image.getpixel((200, 194)), image.getpixel((200, 203))
    ok = sum(top) > sum(bottom) and all(abs(c - 128) <= 12 for c in bottom) and all(abs(c - 64) <= 4 for c in shadow)
    record(ok, "render: button colour", "light top, #808080 bottom, #404040 shadow",
           f"top {top}, bottom {bottom}, shadow {shadow}")

    image = render_1280("ColourLabel", label(colour="#ff0000"))
    red = sum(1 for x in range(100, 700) for y in range(100, 160)
              if (lambda p: p[0] > 200 and p[1] < 60 and p[2] < 60)(image.getpixel((x, y))))
    record(red > 50, "render: label text colour", "red text pixels", f"{red} red pixels")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
width = max(len(t[1]) for t in table)
exp_width = max(len(t[2]) for t in table)
print(f"{'RESULT':<7} {'TEST':<{width}}  {'EXPECTED':<{exp_width}}  GOT")
for result, test, expected, got in table:
    print(f"{result:<7} {test:<{width}}  {expected:<{exp_width}}  {got}")
passed = sum(1 for t in table if t[0] == "PASS")
print()
print(f"Score: {passed}/{len(table)} tests passed")
print("All tests passed" if passed == len(table) else f"{len(table) - passed} test(s) failed")
sys.exit(0 if passed == len(table) else 1)
