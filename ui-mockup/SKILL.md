---
name: ui-mockup
description: The first step for designing or laying out any Roblox UI screen - shop, inventory grid, HUD, menu, popup, game-over or results screen, including "a menu like the one in <other game>". Draws it as PNG mockups at phone, tablet and desktop sizes and checks the layout for overlaps, off-centre elements, text that doesn't fit, things off screen and buttons too small to tap. Use it before roblox-ui builds anything, and whenever the user asks why UI elements overlap, look off-centre or don't fit on phone or other screen sizes, or whether a spec JSON is laid out right. Not for writing Luau that opens or controls UI, building or testing the real UI in Studio once the layout is agreed (roblox-ui), thumbnails, icons or logos, or script bugs like remotes not firing (luau-review).
---

# UI Mockup

Turn a JSON spec of a Roblox UI into PNG mockups at five screen sizes, plus a layout report.
Full design: `C:\AI-Lab\skills-dev\ui-mockup\design.md`.

## Spec format

Positions work like Roblox: `x`/`y` are fractions of the parent, `ox`/`oy` are pixel offsets, and
`anchor` is the AnchorPoint. `w`, `h`, offsets and `textSize` are pixels at 1280x720; the whole page
is scaled by min(width/1280, height/720), like a UIScale.

```json
{ "name": "ShopMenu",
  "elements": [
    { "id": "Panel", "type": "panel", "x": 0.5, "y": 0.5, "anchor": [0.5, 0.5], "w": 760, "h": 480, "centre": true },
    { "id": "Buy", "type": "button", "parent": "Panel", "x": 0.5, "y": 1, "oy": -16, "anchor": [0.5, 1],
      "w": 160, "h": 96, "text": "Buy", "textSize": 28, "centre": "x" } ] }
```

- `type`: `panel`, `button` or `label`. Only buttons and labels have `text`.
- `parent`: another element's `id`; leave it out to sit on the screen. Defaults: x, y, ox, oy 0, anchor [0, 0], textSize from the style.
- `centre`: `true` (both axes), `"x"` or `"y"`. `overhang: true` lets it overlap siblings and stick out of its parent on purpose.
- `textAlign`: `"left"`, `"centre"` (default) or `"right"`, like TextXAlignment. Left-align label columns so they line up.
- `colour`: `"#rrggbb"`. Fill for panels and buttons (buttons keep the gradient and get a darker shadow), text colour for labels. Use it so states differ, e.g. a grey Off toggle.
- Unknown fields are errors, so a typo like `"centred"` can't silently skip a check.

Look (stroke, corner radius, depth, text size, font, colours) comes from
`${CLAUDE_SKILL_DIR}/styles/default.json`. Pass `--style other.json` for another look.
For concrete style and shop-layout numbers taken from tutorials (radius, depth, outline, text size,
item order), read `${CLAUDE_SKILL_DIR}/references/numbers.md`.

## Workflow

1. **Get a spec.** Use the user's SPEC.json, or write one from their description (judgement: keep
   things inside their parents, centre with x 0.5 *and* anchor 0.5) and save it as
   `<project>/mockups/NAME/NAME_spec.json`.
2. **Run it** from the project folder:
   `python "${CLAUDE_SKILL_DIR}/scripts/mockup.py" SPEC.json --project "<project folder>"`
   It writes `<project>/mockups/NAME/NAME_<W>x<H>.png` for each size and `NAME_report.txt`.
   Exit 0 = no failures, 1 = failures, 2 = the spec is broken (empty, missing parent, bad field). Nothing is written on 2.
   **Several screens? Run one first** and check its report and phone PNG before running the rest.
3. **Fix failures** (judgement). Change the spec, never the rules. Fix the cause: a centring failure
   that says "x is 0.5 but anchor isn't" needs the anchor fixed, not an offset. Tell the user about any
   fix they'd notice (moved, removed or reworded things). Failing elements have a red outline. Re-run.
4. **Read the warnings.** `gap` warnings don't fail the run, but fix them unless the closeness is deliberate.
5. **Look at the real output. Required, never skip.** The checks only test numbers; the question is
   "does this look right on a phone?". Open the 640x360 PNG with Read and look for: text too small to
   read, labels that don't line up, states you can't tell apart (On and Off the same colour), cramped
   or empty areas, weak hierarchy. Then the 1920x1080 PNG for text that's tiny inside big buttons.
   **If the report says 0 failures and the image looks wrong, the image is right.** Don't explain it
   away: fix the spec, then find what the checker isn't measuring and make it a check (or a rule).
6. **Show the user** the phone and desktop PNGs and the report's last two lines. Ask them to look once.

## Gates (all must pass before "done")

- The report's last line is `RESULT: 0 failures`. Proof the checks can fail:
  `python "${CLAUDE_SKILL_DIR}/tests/run_tests.py"` runs `tests/good/` (must pass), one `tests/bad/`
  spec per check (each must fail on its own check and no other; empty and missing-parent specs must be
  errors), edge cases either side of each limit, and render tests that read PNG pixels to prove
  `textAlign` and `colour` show up. Finding no spec files fails the run.
  Run it after any change to `mockup.py`; it must say `All tests passed`.
- The user has looked at the phone and desktop PNGs once. A checker can't tell you a screen is ugly.

## Rules

| Rule | Reason |
|---|---|
| `touch_target`: buttons at least 96x96 at 1280x720 (48x48 on a 640x360 phone) | Google's minimum is 48x48dp and Apple's 44x44pt; Roblox UI pixels act like points/dp on phones, so 96 meets both on 640x360 and 667x375 (brain RES-2026-001). Bottom-edge buttons need more (~12mm) |
| `overlap`: siblings never overlap, unless one has `overhang: true` | Overlaps hide content and steal taps; overhang marks the deliberate ones |
| `gap`: siblings at least 8px apart at 1280x720 (warning) | Touching things look cramped and cause mis-taps |
| `corner_clear`: a button pinned to its parent's corner (close, back) is at least 24px from every sibling at 1280x720 | The 8px minimum is for elements in a row; a corner button 10px from a tile passes it and still looks cramped |
| `off_centre`: `centre` elements within 1.5px of the parent's centre | Off by a few pixels looks amateur, and eyes miss it while a script doesn't |
| `outside_parent`: children stay inside their parent unless `overhang: true` | Roblox clips or misplaces them, and it usually means a wrong anchor |
| `off_screen`: nothing sticks out of the screen | Players can't see or tap it |
| `text_fit`: text fits its box at its size, measured in the browser at every size; it never shrinks to fit | Shrunk text gets unreadable on phones |
| An empty spec or a missing parent is an error, never a pass | A report with nothing checked proves nothing |
| Never loosen a rule to make a failure go away | A pass from loosened rules proves nothing |

The numbers live at the top of `scripts/mockup.py`. Change them there, here and in design.md, then run the tests.

## Known problems

Logged here with the date when something can't be fixed straight away. A logged problem is not a
fixed one: fix these before adding features.

- 2026-10-18: gap checks (`gap`, `corner_clear`) measure the box, not the button's drop shadow
  (`depth` in the style), so a gap under a button looks `depth` px smaller than the report says.

## Limits

It's a browser mockup, not Roblox: Arial instead of Roblox fonts, no UIListLayout, UIPadding,
constraints, ZIndex or top-bar inset, and children always draw on top of parents. Check the real
thing in Studio's Device Simulator (roblox-ui).
