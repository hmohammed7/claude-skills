---
name: stable3dgen
description: Generate 3D models locally from an image with Stable3DGen (Hi3DGen) on the user's RTX 3070, then clean, color and export them through Blender for Roblox. Free and offline (no credits). Use when the user wants a 3D model generated from a picture/concept art, or wants AI 3D generation without paid services.
---

# Stable3DGen (local image -> 3D) workflow

Install: `D:\AI\Stable3DGen` (Python 3.10 venv in `.venv`, weights in `weights\`). GPU: RTX 3070 8 GB.
Measured: ~30 s model load + ~76 s per model. Output is **geometry only** (no colors/textures) and very dense (~1M triangles) — always run the Roblox prep step.

Working versions (Windows): torch 2.4.1+cu121, torchvision 0.19.1, xformers 0.0.27.post2, spconv-cu121 2.3.8, diffusers 0.31.0 (newer diffusers breaks on torch 2.4), no triton. Local patches: `import os` added to `hi3dgen/pipelines/hi3dgen.py` (so cached DINOv2 loads offline instead of hanging on GitHub), app.py bound to 127.0.0.1. `generate.py` keeps models on CPU and moves each to the GPU only for its stage — loading everything at once overflows 8 GB and Windows spills to RAM (generation then crawls for 20+ min).

## 1. Get a good input image
- One object, centered, whole object visible, plain or transparent background, 3/4 view, clear silhouette. Background is removed automatically (BiRefNet).
- Sources: the user's image/concept art, a screenshot, or an image generated with an available image tool. Save it under `D:\AI\Stable3DGen\inputs\`.
- Stylized/blocky Roblox-style objects work best; thin parts (wires, hair strands) come out poorly.

## 2. Generate (command line — preferred)
Run in the background (first run downloads several GB of weights and code from Hugging Face/GitHub):
```
cd D:\AI\Stable3DGen
.\.venv\Scripts\python.exe generate.py --image inputs\chest.png --format glb
```
Options: `--image` repeatable (batch in one process), `--out`, `--format glb|obj|stl|ply`, `--seed` (try 2-3 seeds and pick the best), `--ss-steps 50` (lower, e.g. 25, = faster/rougher), `--slat-steps 6`.
Output: `outputs\<name>.glb` + `outputs\<name>_normal.png`. The log prints faces and time.
If CUDA out-of-memory: close other GPU apps (games, Blender viewport in Rendered/Material mode, browsers with heavy tabs), lower `--ss-steps`, and run one image per process.

Web UI alternative for the user: `.\.venv\Scripts\python.exe app.py`, then open http://127.0.0.1:7860 (local only).

## 3a. One-command Roblox prep (headless Blender, no MCP needed)
```
cd D:\AI\Stable3DGen
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b -P tools\roblox_prep.py -- --in outputs\<name>.glb --out-fbx "D:\Roblox MCP\assets\models\<Name>.fbx" --tris 10000 --height 6
```
Joins, cleans (merge doubles, loose, normals), decimates to `--tris` (Roblox max 20,000; 5-10k good for hero props, ~2k for small props), scales to `--height` studs, origin bottom-center, smooth shading (`--flat` for low-poly look), exports FBX + `.blend` + `_preview.png`. Always `Read` the preview PNG to check the shape before handing it over.

## 3b. Manual / artistic cleanup in Blender (Blender MCP, see `blender-roblox`)
1. Import: `bpy.ops.import_scene.gltf(filepath=r"D:\AI\Stable3DGen\outputs\<name>.glb")`.
2. Check with `look`. Generated meshes are often 200k-1M+ triangles.
3. Merge by distance, delete loose pieces, recalc normals, then Decimate (Collapse) to the Roblox budget (props 500-5,000 tris, hard limit 20,000 per mesh). Consider Remesh (voxel) first if the topology is messy, then decimate.
4. Scale to studs (1 unit = 1 stud), put the origin at bottom center, apply transforms.
5. Color it: Smart UV Project + paint/flat materials, or vertex colors; for PBR bake textures (see `blender-roblox`).
6. Export FBX to `D:\Roblox MCP\assets\models\` and save the .blend to `assets\blend\`.

## 4. Into Roblox
User imports the FBX in Studio (Import 3D); then set it up and verify with Studio MCP (see `blender-roblox`).

## Notes
- MIT licensed; generated assets can be used in the user's games.
- Runtime downloads come from official sources: Hugging Face (Stable-X, ZhengPeng7/BiRefNet) and torch.hub (facebookresearch/dinov2, hugoycj/StableNormal).
- Don't run generation while Roblox Studio playtests or Blender renders heavy scenes — they share the 8 GB GPU.
