---
name: roblox-vfx
description: Create Roblox visual effects and game feel — ParticleEmitters, Beams, Trails, Highlights, lighting flashes, TweenService animation, camera shake, hit-stop and screen effects — with client-side playback triggered from the server. Use when adding juice, impacts, abilities, pickups, explosions, auras or any visual polish.
---

# Roblox VFX and game feel

## Architecture
- Server decides *that* something happened; clients play the effect. Fire a RemoteEvent (e.g. `Remotes.PlayVFX:FireAllClients("Explosion", position)`), and a client `VFXController` module spawns the effect locally. This keeps the server cheap and effects smooth.
- Store effect templates in `ReplicatedStorage.Shared.VFX` (build templates once with MCP and save the place, or construct them in code). Clone, parent, `:Emit()`, then `Debris:AddItem(clone, lifetime)`.
- One-shot effects: `ParticleEmitter.Enabled = false` + `emitter:Emit(count)`. Continuous auras: `Enabled = true`.

## Building blocks
| Effect | Instance | Key properties |
|---|---|---|
| Sparks, smoke, dust, magic | ParticleEmitter (in Attachment) | Rate/Emit, Lifetime, Speed, SpreadAngle, Size & Transparency NumberSequences, Color ColorSequence, LightEmission 1 for glow, Drag, Acceleration, Rotation/RotSpeed, Squash, FlipbookLayout for animated textures |
| Lasers, lightning, links | Beam (Attachment0/1) | Width0/1, CurveSize0/1, TextureSpeed, LightEmission, Segments |
| Swings, dashes, projectiles | Trail (two attachments) | Lifetime, WidthScale, MinLength |
| Outline/selection | Highlight | FillTransparency, OutlineColor, DepthMode |
| Flash | PointLight/SpotLight tweened Brightness | |
| Shockwave | Neon/ForceField part tweened Size + Transparency | |
| Screen | ColorCorrection / Blur in Lighting tweened briefly | |

## Juice checklist per player action
1. Anticipation (tiny wind-up tween or sound)
2. Impact: particles + flash + sound + small camera shake
3. Feedback number/text popup (BillboardGui tweened up and faded)
4. Settle: lingering smoke/sparkle, easing out (`Enum.EasingStyle.Quad/Back/Elastic`)
Keep effects short (0.2-0.8 s) for frequent actions, bigger for rare ones (level up, rare drop).

## Camera shake (client)
```lua
local RunService = game:GetService("RunService")
local function shake(intensity: number, duration: number)
	local cam = workspace.CurrentCamera
	local t = 0
	local conn; conn = RunService.RenderStepped:Connect(function(dt)
		t += dt
		local fade = 1 - math.min(t / duration, 1)
		cam.CFrame *= CFrame.new((math.random() - 0.5) * intensity * fade, (math.random() - 0.5) * intensity * fade, 0)
		if t >= duration then conn:Disconnect() end
	end)
end
```

## Quality and performance
- Cohesive palette: effects use the game's palette + one accent color per element/rarity.
- Respect settings: offer a "reduce effects" toggle; scale particle counts by `UserGameSettings().SavedQualityLevel` if needed.
- Cap simultaneous emitters; always clean up clones (Debris) and disconnect RenderStepped connections.
- Verify with a playtest + `screen_capture`; describe what each effect looks like in the QA report.
- Textures: search Creator Store via `search_asset` for particle textures/flipbooks, or `generate_texture`.
