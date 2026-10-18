---
name: roblox-building
description: Build Roblox worlds, maps, props and models through the Roblox Studio MCP — procedural building with execute_luau, AI mesh/material/texture generation, Creator Store assets, lighting and atmosphere, terrain, and performance-safe composition. Use for any modeling, level design, environment art or lighting task.
---

# Roblox world building and modeling (via Studio MCP)

## Tool choice
| Need | Tool |
|---|---|
| Blockout, layouts, repeated structures, terrain | `execute_luau` (procedural Luau in Edit mode) |
| Parametric props (furniture, buildings, vehicles) | `generate_procedural_model` |
| Unique organic/hero model | `generate_mesh` (then `segment_mesh` if parts must be split) |
| Custom surface look | `generate_material`, `generate_texture` |
| Existing quality asset | `search_asset` -> `insert_asset` (prefer Roblox-verified / high-rated, check it contains no scripts you didn't expect) |
| Check result | `screen_capture` with camera_position + look_at_position from 2-3 angles |
| Find/inspect | `search_game_tree`, `inspect_instance` |

Always run building code in the **Edit** datamodel, never during a playtest (changes are lost on stop).

## Workflow
1. Blockout: grey anchored parts for layout, scale (character is ~5 studs tall, doors 8+ studs, paths 10+ studs wide), and sight lines. Screenshot.
2. Landmarks: one tall, distinctive object per zone so players can navigate.
3. Detail pass: swap blockout for models/meshes; vary size, rotation and color slightly to avoid repetition.
4. Lighting and atmosphere (below). Screenshot again from player height (~6 studs above ground).
5. Group into Models/Folders with clear names (`Map/Zone1/Props`). Tag repeated interactive things with CollectionService instead of copying scripts.
6. Tell the user to save the place.

## Procedural building pattern (execute_luau)
```lua
local folder = workspace:FindFirstChild("Map") or Instance.new("Folder")
folder.Name = "Map"; folder.Parent = workspace
local function part(props)
	local p = Instance.new("Part")
	p.Anchored = true; p.TopSurface = Enum.SurfaceType.Smooth; p.BottomSurface = Enum.SurfaceType.Smooth
	for k, v in props do (p :: any)[k] = v end
	p.Parent = props.Parent or folder
	return p
end
-- make building code idempotent: clear the previous version before rebuilding
```
Make builds re-runnable: destroy the previous generated folder first so iterations don't stack duplicates.

## Lighting and art direction
- Lighting set in `default.project.json` is enforced by Rojo — change lighting there (e.g. `"Technology": "Future"`), not via MCP, or it will be reverted.
- Add under Lighting (via project json or MCP if not managed by Rojo): `Atmosphere` (Density 0.3, Haze 1-2), `Bloom` (subtle), `ColorCorrection` (slight saturation/contrast), `SunRays`, optional `DepthOfField` for menus.
- Pick a 3-5 color palette per game and reuse it. Materials: SmoothPlastic for stylized, realistic materials (Wood, Slate, Concrete) for grounded looks — don't mix styles randomly.
- Terrain: `workspace.Terrain:FillBlock / FillBall / FillRegion` for ground, water, hills.

## Performance
- Anchor everything static; set `CanCollide=false`, `CanTouch=false`, `CanQuery=false` on decorative parts.
- Prefer MeshParts/unions sparingly; use `RenderFidelity=Automatic`, `CollisionFidelity=Box` for decor.
- Keep part count reasonable (aim < 10k for mobile-friendly maps); enable `StreamingEnabled` for large maps.
- Use the Studio MCP `skill` `rbx-scene-analysis` to audit heavy scenes.
