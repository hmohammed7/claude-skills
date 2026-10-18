---
name: luau-review
description: Review Roblox Luau code for the mistakes that break games (trusting the client, unchecked remote arguments, loops without waits, scattered magic numbers, swallowed pcall errors, bad asset ids). Use when the user asks to review, check or audit Roblox Luau or a game script, or asks why a remote or script "does nothing". Not for writing new code.
---

# Luau Review

Review only. Do not write new features or rewrite files. Report problems and their fixes.

## Checklist

1. **Server never trusts the client.** Prices, damage, cooldowns and rewards are
   decided or checked on the server, not just accepted from what the client sends.
2. **Remote arguments are checked.** Every RemoteEvent/RemoteFunction handler checks
   each argument's type (`typeof`) and range before using it.
3. **No infinite loops without a wait.** Every `while true do` / `repeat` loop yields
   (`task.wait()`, an event `:Wait()`, etc.) on every pass.
4. **Tunable numbers live in a Config module.** Prices, speeds, cooldowns, damage and
   rewards are not hard-coded and scattered through scripts.
5. **pcall wraps the whole risky block.** The pcall covers every line that can fail
   (e.g. the full DataStore read/write), not one line inside it, and the failure is
   printed (`warn`) or handled, never silently ignored.
6. **Asset ids are strings.** Where an asset is expected (Image, SoundId, MeshId,
   Texture, AnimationId...), the value is `"rbxassetid://123"`, not a bare number.

## How to review

- Find every script in scope (Rojo `src/` files, or Studio scripts via the Studio MCP).
- Go through EVERY checklist item for EVERY file. Mark each PASS or FAIL, even when it
  passes. Never skip an item. If an item doesn't apply (e.g. no remotes), mark it
  PASS (n/a) and say why.
- Read the code. Never guess what a line does. Cite real line numbers.

## Output

For each file, a PASS/FAIL table:

| # | Item | Result |
|---|------|--------|
| 1 | Server never trusts client | PASS / FAIL |

Then for each problem:

- **File:line** - `path/to/Script.server.luau:42`
- **Item:** checklist number and name
- **Why it matters:** one sentence
- **Fix:** the corrected code or the exact change

End with `N problems found`.
If there are none, say "0 problems found" and list the files and items you checked.
