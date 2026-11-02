# Alpine rehearsal nook — Blender and FBX delivery

This is an editable 3D interpretation of the approved isolated corner concept. Each prop or functional assembly is a separate named mesh, with its own non-overlapping UV0 atlas and unique baked textures. Small construction components such as piano keys remain separate mesh islands within the piano asset; cushions, books, scores and instruments are separate reusable assets.

## Files

- `Rehearsal_Nook.blend` — assembled scene, separate objects, packed textures, camera, warm key light, cool fill, rim light and piano lamp.
- `fbx/Rehearsal_Nook_Assembled.fbx` — assembled scene meshes with embedded textures. Studio ground and render-only lights/camera are excluded.
- `fbx/objects/` — one FBX per asset, textures embedded, ground-centered local pivot. Rotation is applied; units are meters. Assembly transforms are recorded in `asset-manifest.json`.
- `textures/` — every texture as an individual PNG: `_BaseColor`, `_Roughness`, `_Metallic` per object.
- `uv-layouts/` — separate SVG UV wireframes for repainting.
- `sketchfab/Rehearsal_Nook_Assembled.glb` — optional self-contained PBR alternative.
- `previews/` — actual Blender renders of the scene.
- `source/` — reproducible Blender construction and texture/export scripts, plus source `.blend` files with procedural painted materials before baking.
- `asset-manifest.json` — object names, geometry counts, texture sizes, assembly locations and lighting values.
- `validation-report.json` — FBX embedding checks and an assembled FBX reimport check.

## Texture treatment

The color maps contain broad, low-frequency painterly color variation, darker lower regions and brighter colors painted onto the modeled bevel faces. They are baked from authored Blender materials into each object's UV map, so this treatment survives FBX export. The finish is deliberately clean rather than distressed or speckled. These are procedurally authored painterly textures, not a projection of the concept painting.

Base Color uses sRGB. Roughness and Metallic use non-color data. All maps use the object's UV0. Bevels, instrument rims, fabric folds, leaves and basket weave are modeled; no normal-map dependency is required. Texture sizes are 512, 1024 or 2048 pixels according to the asset. Geometry and textures are supplied for further art direction and optimization; headset frame rate has not been tested.

## Sketchfab upload

1. Upload `Sketchfab_Upload.zip` supplied next to this folder. It contains the assembled FBX and the external PNG maps as a fallback for its embedded textures. Alternatively upload the assembled FBX directly.
2. Open the model's 3D settings and choose a lit PBR presentation. Keep the mesh as separate material groups.
3. Check a wood object and the brass lamp. If automatic material mapping needs adjustment, assign that object's `_BaseColor.png` to Base Color, `_Roughness.png` to Roughness and `_Metallic.png` to Metalness. Use roughness directly; invert only if the selected viewer channel is explicitly glossiness.
4. Use a warm studio environment, a broad warm key from above/front-left, and a weaker cool fill from front-right. Enable moderate contact shadows/ambient occlusion. Keep bloom restrained. The `.blend` contains the original area-light setup; its exact renderer lighting is not carried by the mesh-only FBX. Numerical light positions and colors are in `asset-manifest.json` for reference, but viewer light intensity scales differ.
5. Set the initial view to the open corner, looking down slightly, matching `previews/02_final_beauty.png`. Frame the full floor slab and top of the walls. Use a warm off-white background.
6. Check the piano keys, music scores, plant leaves and fabric from several angles before publishing. The mountain view is a separate stylized insert; it can be hidden/replaced if you prefer a transparent window and a different environment.

The optional GLB preserves the same PBR maps in a self-contained format if you prefer that upload path. Nothing has been uploaded or published to your account.

Sketchfab references: [upload integration guidelines](https://sketchfab.com/developers/guidelines), [supported formats](https://sketchfab.com/features), and [viewer material and lighting adjustments](https://sketchfab.com/blogs/community/getting-your-sketchup-models-to-sketchfab-the-right-way/).

## Rebuilding

Open `source/Rehearsal_Nook_UV_Source.blend` and run `source/texture_export.py` to reproduce the final texture/export stage. For a complete rebuild, run `source/build_nook.py` in Blender first. The scripts resolve output paths relative to this delivery folder. Use a duplicate folder for experimentation, as rebuilding writes the named outputs again.
