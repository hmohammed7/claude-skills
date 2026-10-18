---
name: blender-roblox
description: Model, texture and export 3D assets in Blender (via the Blender MCP) for use in Roblox - modeling with bpy, asset libraries and AI generation, low-poly optimization, UVs and PBR textures, and FBX export plus Roblox 3D Importer / SurfaceAppearance setup. Use when the user wants a custom model, prop, weapon, vehicle or character made in Blender, or anything Blender-related.
---

# Blender -> Roblox asset workflow

Blender MCP tools: `get_addon_status`, `get_scene_info`, `execute_blender_code` (full bpy), `look` (viewport/render image), `search_assets` / `import_asset` (Poly Haven, Sketchfab, Poly Pizza), `generate_3d` (one textured model from text/image; may cost the user credits - ask first).
Requires Blender open with the "MCP for Blender" add-on enabled and connected (N panel > MCP for Blender > Connect). If tools fail, ask the user to check that.

## Choose the source
1. Simple/stylized/geometric props -> model procedurally with `execute_blender_code` (fast, exact, low-poly).
2. Realistic or common objects -> `search_assets` then `import_asset` (check license; Poly Haven is CC0).
3. Unique hero object from a picture -> local, free `stable3dgen` skill (preferred), or `generate_3d` (paid; confirm cost with the user), then clean up.
Prefer Roblox-native building (`roblox-building`) when parts/unions are enough; use Blender when shape quality matters.

## Modeling rules for Roblox
- Scale: treat 1 Blender unit as 1 stud while modeling (Roblox character ~5-6 studs tall). Verify the imported size in Studio and rescale in the importer if needed.
- Budget: <= 20,000 triangles per mesh (Roblox limit); aim far lower for props (100-2,000) so mobile runs well. Use Decimate / remove hidden faces.
- Apply transforms (scale/rotation) before export; set origin at the logical pivot (bottom center for props, hinge for doors).
- Clean geometry: no n-gons problems (triangulate on export), recalc normals outward, merge by distance, no loose verts.
- Split into separate meshes only where Roblox needs separate parts (moving pieces, different collision).
- Name objects clearly; the names become MeshPart names.

## Materials and textures
- Stylized: flat colors via vertex color/simple material, or a small palette texture (many objects share one texture atlas).
- PBR: bake to ColorMap (albedo), NormalMap (OpenGL), RoughnessMap, MetalnessMap, 1024x1024 max (512 for small props). In Roblox apply via a `SurfaceAppearance` on the MeshPart.
- One material per mesh where possible.
- Check with `look` from multiple angles before exporting.

## Export
Run in `execute_blender_code`:
```python
import bpy, os
out = r"D:\Roblox MCP\assets\models"
os.makedirs(out, exist_ok=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(out, "AssetName.fbx"), use_selection=True,
    apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', use_mesh_modifiers=True,
    mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True)
```
Save textures as PNG next to it. Also save the .blend in `assets/blend/` so the asset is editable later (both folders can go in Git; large binaries may need Git LFS).

## Into Roblox
- The user imports in Studio: Avatar/Home tab > Import 3D (or File > Import 3D), picks the FBX, checks scale and "Anchored", then Import. (Uploading meshes requires their Roblox account, so the user does this step.)
- After import, use Studio MCP: find the MeshPart (`search_game_tree`), set CollisionFidelity (Box/Hull for props), RenderFidelity Automatic, add SurfaceAppearance with uploaded texture IDs, then `screen_capture` to verify in context.
- For moving parts or rigs, keep the Blender hierarchy and rig simple; Roblox supports skinned meshes with bones from FBX.
