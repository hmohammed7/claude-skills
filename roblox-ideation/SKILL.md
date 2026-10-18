---
name: roblox-ideation
description: Generate, evaluate and choose Roblox game concepts, then turn the winner into a one-page game design doc with core loop, progression, monetization fit and A+ acceptance criteria. Use when the user wants game ideas, is choosing between ideas or features, or needs design decisions made.
---

# Roblox ideation and decision making

## 1. Generate concepts (give 3-5)
For each concept write:
- **Hook (one sentence a 12-year-old would repeat to a friend)**
- **Core loop** (the 30-second action repeated forever) -> **meta loop** (what you spend rewards on) -> **long-term goal**
- **Genre lineage**: which proven Roblox genre it builds on (simulator, tycoon, obby, tower defense, horror/co-op, survival, fighting/battlegrounds, roleplay/life, anime action, "grow a ..."/idle, party/minigames) and the twist
- **Social glue**: why playing with friends is better (co-op, trading, showing off, competing)
- **Thumbnail test**: describe the thumbnail; if it isn't instantly readable and exciting, the concept is weak
- **Scope**: solo-dev weeks to MVP

Techniques: genre x twist mashups, "verb first" (pick a satisfying verb: smash, grow, launch, collect, escape), trend + evergreen (trending theme on a proven loop), and inverting a popular game.

## 2. Score and choose
Score each 1-5 and show the table:

| Criterion | Weight |
|---|---|
| Hook clarity / thumbnail appeal | 3 |
| Core loop fun in first 60 s | 3 |
| Retention depth (progression, collection, social) | 2 |
| Monetization fit without pay-to-win | 2 |
| Feasible for this dev (scope, skills, assets via MCP) | 2 |
| Differentiation from top competitors | 1 |

Recommend the top score, state the main risk, and how the MVP tests that risk.
For close calls or big strategic choices, load `council` (four-voice debate) or `product-lens` (go/no-go), then decide — do not stall.

## 3. Decision rules of thumb
- Fun first: if the core loop isn't fun with grey boxes, art won't save it.
- Ship a vertical slice before any content breadth.
- First 60 seconds: player must understand the goal and get a reward. First 5 minutes: first upgrade/unlock. First session: a reason to come back (daily reward, unfinished goal, friend invite).
- Mobile is the majority of players: touch controls and readable UI are non-negotiable.
- Prefer systems that generate content (procedural, upgrades, rarity tiers) over hand-made content when solo.
- Record important decisions in `docs/decisions.md` (date, decision, why, alternatives).

## 4. GDD template (write to docs/GDD.md)
```
# <Game name>
Hook:
Target player / session length:
Core loop:          Meta loop:          Long-term goal:
Systems (one ModuleScript each): <name: responsibility>
Remotes: <name: client->server intent, server validation>
Saved data (DataStore schema v1):
UI screens: HUD, shop, inventory, settings, ...
World: zones, landmarks, art direction (palette, materials, lighting mood)
Juice list: VFX/SFX per player action
Monetization: game passes, dev products, premium benefits (no pay-to-win)
MVP scope (vertical slice):
Acceptance criteria (testable):
A+ rubric overrides (if any) for roblox-qa-loop:
```
