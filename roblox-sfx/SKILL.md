---
name: roblox-sfx
description: Add sound design and music to Roblox games — finding licensed audio in the Creator Store, SoundGroups and mixing, 3D positional sound, UI sounds, pitch variation, music playlists and ambience. Use when adding SFX, music, ambience or audio polish.
---

# Roblox sound design

## Sourcing audio
- Use `search_asset` (audio) for Creator Store sounds; prefer Roblox-uploaded / licensed library tracks (free to use). Audio uploaded by others may be private and fail to load — verify in a playtest (`get_console_output` shows "Failed to load sound" errors).
- Keep a single `Sounds.luau` registry in `src/shared` mapping names to `rbxassetid://` IDs, so swapping a sound is one line.

## Structure
- `SoundService` with SoundGroups: `Master` -> `Music`, `SFX`, `UI`, `Ambience`. Every Sound sets `SoundGroup`. Settings menu sliders change group volumes.
- 3D sounds: parent the Sound to a Part/Attachment in the world (RollOffMode InverseTapered, RollOffMin/MaxDistance tuned). 2D sounds (UI, music): parent to SoundService or PlayerGui.
- Play one-shots on the client for responsiveness (same remote pattern as VFX); clone the template, `:Play()`, destroy on `Ended`.
- Randomize `PlaybackSpeed` 0.9-1.1 on repeated sounds (footsteps, hits, coins) to avoid fatigue.

## What needs sound (minimum)
- UI: hover, click, open/close, purchase success, error, reward/level-up fanfare
- Core verb: every hit/collect/place/shoot has a satisfying sound, scaled up for crits/rare drops
- World: ambience loop per zone, fade between zones
- Music: calm loop for lobby, energetic for action, short stinger for wins/losses; crossfade with TweenService on Volume

## Mixing guide (starting volumes)
Music 0.3-0.4, ambience 0.2-0.3, SFX 0.5-0.7, UI 0.4-0.5. The core-verb sound should be the clearest thing in the mix.
Use `EqualizerSoundEffect`, `ReverbSoundEffect` (caves/halls), `CompressorSoundEffect` on Master if loud moments clip.

## Verify
Playtest, check the console for failed loads, and confirm the volume hierarchy makes sense. Note in the QA report which actions still have no sound.
