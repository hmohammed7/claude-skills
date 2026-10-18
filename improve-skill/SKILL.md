---
name: improve-skill
description: Turn a correction into a permanent improvement to one of my Claude Code skills, as a check, a rule or a note, then test and commit it. Use when I say a skill got something wrong and I'd hate to catch it again, "turn that into a rule/check", "make the skill remember this", "improve the skill", "add that to the skill", when a skill's checker passed something that looks wrong, or when I want to roll a skill back to an earlier version. Not for making a brand-new skill (skill-creator) or fixing the output itself without changing the skill.
---

# Improve a skill

Great skills aren't designed, they're corrected: every time one does something wrong, the fix goes
**into the skill**, with the reason. Skills live in `C:\Users\hasee\.claude\skills`, a Git repository.

## The loop

1. The skill is used on real work and gets something wrong. Get the exact description of what was
   seen ("the close button is 10px from the tile, it looks cramped"), not "make it better".
2. Fix the output first (the spec, the file, the code), so the job at hand is done.
3. Ask: would we hate to catch this again? If not, stop. If yes, pick one kind of fix:

| Kind | Use when | Goes in | Example |
|---|---|---|---|
| **Check** | It can be measured | the skill's script, plus a bad test spec that proves the check fails | "Buttons at least 88px" became `touch_target` |
| **Rule** | It needs judgement | `SKILL.md`, one line with the reason | "Never shrink text to make it fit. Widen the box or shorten the text." |
| **Note** | Detail only some jobs need | `references/<topic>.md`, linked from SKILL.md | a technique only tutorials use |

   **Prefer a check over a rule when it can be measured**: checks never forget, rules are next,
   notes keep SKILL.md from bloating.
4. Make the change:
   - Check: add it to the script (numbers as named constants at the top), add `tests/bad/<name>.json`
     that breaks only this check, list it in the test runner, and add edge cases either side of the limit.
     Also add the rule row to SKILL.md so the reason is written down.
   - Rule: one line, the rule then the reason. Say where it stops applying if that's the trap
     ("the 8px minimum is for elements in a row, not a button in a corner").
   - Note: put the detail in `references/`, and one line in SKILL.md saying when to read it.
   - If the skill has a design doc or a second copy (e.g. `C:\AI-Lab\skills-dev\<skill>`), update it to match.
5. Run the skill's tests. A new check must fail on its bad spec and the good specs must still pass.
   If a good spec now fails, look at it: a real problem gets the spec fixed, not the check loosened.
6. Commit (see below) and show me the diff (`git show --stat HEAD` and the SKILL.md part of `git show HEAD`).

## When the checker and your eyes disagree, believe your eyes

If the report says 0 failures and the output looks wrong, the output is right. Don't argue with it or
explain it away. Find out what the checker isn't measuring and decide whether to add a check.
Most checks exist because something passed that shouldn't have.

## Log it, then fix it

If a problem can't be fixed right now, write it in that skill's SKILL.md under `## Known problems`,
with the date: `- 2026-10-18: <what's wrong and when it shows up>`. A logged problem is not a fixed
problem: go back to the list and fix these before adding features. A long Known problems section is a
skill that's quietly failing.

## Keep versions

After **any** change to a skill, commit it from `C:\Users\hasee\.claude\skills`:

```
git add -A
git commit -m "<skill>: <what changed>, since <why>"
```

One line saying what changed and why. To see history: `git log --oneline -- <skill>`. To roll a
skill back when an "improvement" made it worse: `git checkout <commit> -- <skill>` then commit that
as "<skill>: roll back <what>, since <why>". Never use `git reset --hard` or force anything; old
versions stay in the history. `synced/` is managed by the Claude app and is not tracked.
