---
name: brain
description: My Obsidian brain vault at C:\AI-Lab\brain (projects, lessons, research, resources, people and tools). LOAD it at the start of every session before working. SYNC it right after a decision is made, a project status changes, a problem is found or fixed, I correct you, a new person or tool comes up, or an open loop is opened or closed. SEARCH it when I ask what we know, decided or learned about something - e.g. "what do we know about X", "what did we decide about X", "did we learn anything about X", "check the brain", "remember this", "save that", "add this to the brain", "don't do that again", "that's wrong, do it like this", "what's my current focus", "what's still open".
---

# Brain

Vault: `C:\AI-Lab\brain` (override with the `BRAIN_PATH` env var). Helper script:

```
python "${CLAUDE_SKILL_DIR}/scripts/brain.py" <command>
```

Commands: `next-id PREFIX`, `search WORDS...`, `add NOTE.md`, `log ACTION ID TEXT`, `check`.

## Vault layout

| Folder | Type | Id prefix | Template |
| --- | --- | --- | --- |
| 10 Projects | project | PRJ | 00 System/Templates/Project.md |
| 20 Lessons | lesson | LES | 00 System/Templates/Lesson.md |
| 30 Research | research | RES | 00 System/Templates/Research.md |
| 40 Resources | resource | REF | 00 System/Templates/Resource.md |
| 50 People and Tools | entity | ENT | 00 System/Templates/Entity.md |
| 90 Inbox | drafts (not registered) | - | - |

Every note starts with this frontmatter (all fields filled):

```
---
id: PRJ-2026-001
type: project
status: active          # active | paused | done | archived
created: 2026-10-17
updated: 2026-10-17
value: high             # critical | high | medium
summary: One sentence, no "|" characters.
---
```

`Brain Root.md` (id ROOT-2026-001) holds Current focus, Active projects, Open loops and Recent decisions.
CHANGELOG actions are one uppercase word: CREATED, UPDATED, ARCHIVED.

## LOAD (start of a session)

1. Read `Brain Root.md`.
2. Read the last 10 lines of `CHANGELOG.md`.
3. Run `search` with the main word(s) of the task's topic.
4. Read the top 1-2 notes it returns. Nothing else.

Use what you learned quietly. Don't recite it back to me.

## SYNC (after something worth keeping happens)

Only save facts: decisions, status changes, problems found or fixed, corrections, new people/tools, open loops.
**Never save brainstorming, dead ends or guesses.** If unsure whether it's real or worth keeping, write a
draft note in `90 Inbox`, tell me it's there, and stop.

1. `search` first. If a note already covers it, update that note (bump `updated:`) instead of making a new one.
2. New note: `next-id PREFIX` for the id.
3. Write the note from its template into the right folder. Fill every frontmatter field.
4. `add "<folder>/<Note>.md"` to add or replace its registry line.
5. `log CREATED|UPDATED <id> <what changed>`.
6. If focus, project status, decisions or open loops changed, update `Brain Root.md` (bump `updated:`),
   keep it under 40 lines by removing the oldest rows, then `log UPDATED ROOT-2026-001 <what changed>`.
7. `check` - it must say `0 problems`. Fix anything it reports before moving on.
8. Tell me in one line what was saved.

A correction from me becomes a lesson note (20 Lessons, LES) with `## Rule`, `## Why`, `## How to apply`.

## SEARCH (when I ask what we know / decided / learned)

1. Run `search` with the key word(s). Try a synonym or single word if nothing comes back.
2. Read the top 1-3 notes it returns.
3. Answer with the facts and cite the note ids (e.g. "per LES-2026-001 ...").

If nothing is found, say so plainly. Never fill gaps with guesses.
