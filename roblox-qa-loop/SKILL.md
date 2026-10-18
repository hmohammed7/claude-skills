---
name: roblox-qa-loop
description: Build -> playtest -> grade -> fix loop for Roblox, repeated until the feature or game scores A+ with zero errors. Roblox version of ECC's gan-style-harness - a separate strict roblox-evaluator agent tests the live game through the Studio MCP (playtests, console, screenshots, simulated input) and grades against a rubric; the builder fixes and repeats. Use when the user wants something finished, polished, "problem free", "A+", or tested until it works.
---

# Roblox QA loop (generator / evaluator until A+)

Core idea from ECC `gan-style-harness`: the builder is too optimistic about its own work, so a **separate evaluator** with fresh context grades it strictly. The builder only builds, the evaluator only critiques.

## Setup (once per task)
1. Write `qa/spec.md`: what is being built, acceptance criteria (each one testable in a playtest), and anything from `docs/GDD.md`.
2. Write `qa/rubric.md` (copy the default below; adjust weights for the task, e.g. a backend system weighs Functionality higher).
3. Limits: **max 6 iterations** by default (the user can raise it). Stop early on a plateau: same score 2 iterations in a row -> report to user with the blocking issues.

## Each iteration
1. **Build/fix** (you): implement or fix in `src/` (Rojo) and the world (MCP). Fix *every* issue from the last report, highest severity first. Don't touch the rubric or spec to make grading easier.
2. **Smoke check** (you): confirm Rojo synced (`script_read` / `search_game_tree`), make sure Studio is in Edit mode.
3. **Evaluate** (fresh agent): spawn the `roblox-evaluator` agent with the spec path, rubric path, iteration number and studio_id. It playtests and returns its report as text (subagents may not be allowed to write files); **you save it verbatim to `qa/report-NNN.md`**. The report has scores, letter grade and a numbered issue list. If the `roblox-evaluator` agent type isn't available (agents load at session start), spawn a `general-purpose` agent told to read `~/.claude/agents/roblox-evaluator.md` and act as it, loading the Studio MCP tools via ToolSearch. Do not evaluate yourself and do not argue with its findings — fix them or, if a finding is genuinely wrong, note why in `qa/log.md`.
4. **Log**: append iteration number, weighted score, grade, and top issues to `qa/log.md`.
5. Pass check: **A+ = weighted score >= 9.0 AND no criterion below 8 AND zero errors/warnings from game scripts AND every acceptance criterion verified in a playtest.** If passed, stop; otherwise next iteration.

If the Agent tool is unavailable, run the evaluator checklist yourself in a clearly separate step, and be harsher than feels natural.

## Default rubric (each 1-10)
| Criterion | Weight | 9-10 means |
|---|---|---|
| Functionality | 0.30 | Every acceptance criterion works in playtest, edge cases handled (rejoin, spam clicks, dying, leaving mid-action), no console errors |
| Game feel | 0.20 | Every action has responsive VFX/SFX/UI feedback; controls feel tight |
| Visual quality | 0.15 | Cohesive art direction, good lighting, no z-fighting/floating parts, readable from player camera |
| UX / UI clarity | 0.15 | New player knows what to do in 10 s; works on phone layout; no clipped text |
| Robustness & security | 0.10 | Server-authoritative, remotes validated, data saves safely, no memory leaks/unbounded loops |
| Performance | 0.10 | No frame drops in normal play, reasonable part/instance counts, no per-frame server work without need |

Grades: A+ >= 9.0, A >= 8.5, B >= 7.5, C >= 6.5, D >= 5, F < 5.

## Anti-gaming rules
- Never weaken the rubric, spec, or tests mid-loop. Never suppress errors (`pcall` swallowing, deleting warnings) to look clean — fix the cause.
- Errors from third-party Studio plugins (e.g. paths starting with `cloud_` or a plugin name) don't count against the game; list them separately.
- The evaluator must interact with the game (move, click, trigger features), not just read code.
- Always stop the playtest at the end of each evaluation so building code runs in Edit mode.

## Final report to the user
Iterations run, score progression, final grade, what was verified, known limitations, and a reminder to save/publish the place.
