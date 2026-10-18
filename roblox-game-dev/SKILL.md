---
name: roblox-game-dev
description: Master pipeline for making a Roblox game end to end — idea, design decisions, code, world building, VFX, UI, SFX, testing, monetization, launch and marketing. Use at the start of any Roblox game or big feature to pick the right phase and the right specialised roblox-* skill.
---

# Roblox game development pipeline

Use this as the router. Each phase names the skill to load. Work in a Rojo project (load `rojo` for every code task).

| Phase | Goal | Load |
|---|---|---|
| 1. Ideate | Pick a concept worth building | `roblox-ideation` |
| 2. Decide | Resolve big tradeoffs (scope, genre, monetization) | `roblox-ideation` (decision section), `council` |
| 3. Design doc | One-page GDD with core loop + acceptance criteria | `roblox-ideation` (GDD template) |
| 4. Code systems | Server/client modules synced by Rojo | `rojo` |
| 5. World & models | Map, props, lighting, terrain | `roblox-building`; custom meshes in Blender: `blender-roblox` |
| 6. VFX & juice | Particles, beams, tweens, camera feel | `roblox-vfx` |
| 7. UI | HUD, menus, shop, mobile-ready | `roblox-ui` |
| 8. Sound | SFX, music, ambience | `roblox-sfx` |
| 9. Quality loop | Build -> test -> fix until A+ | `roblox-qa-loop` |
| 10. Monetize & launch | Passes, products, thumbnails, ads, updates | `roblox-launch-marketing` |

## Default workflow for "make me a game"
1. Load `roblox-ideation`; produce 3 concepts, score them, recommend one. If the user already gave a clear idea, skip to the GDD.
2. Write `docs/GDD.md` in the project (core loop, systems, remotes, data, UI screens, acceptance criteria, A+ rubric).
3. Build an MVP vertical slice first: the core loop playable end to end, ugly is fine.
4. Run `roblox-qa-loop` on the slice until it passes.
5. Layer polish in order: world -> UI -> VFX -> SFX. Re-run the QA loop after each layer.
6. Add progression, retention hooks, monetization; QA loop again.
7. Prepare launch assets with `roblox-launch-marketing`.

## Always
- Code as files via Rojo; world/assets via Studio MCP. Remind the user to **save the place** (File > Save / Publish) after MCP builds things — those live in the place file, not in Git.
- Look up APIs you are unsure about with the Studio MCP `skill` tool (`rbx-docs-search`) instead of guessing.
- Other Studio MCP skills worth loading when relevant: `rbx-debug` (breakpoints), `rbx-unit-test`, `rbx-perf-profiling`, `rbx-scene-analysis`, `rbx-device-simulator-lua`.
- Keep the user in control of irreversible actions: publishing, spending Robux, enabling API/HTTP settings, changing game permissions.
- Roblox Community Standards and age guidelines apply to everything (no gambling-like paid random rewards without disclosure, no off-platform links, no real-money trading).
