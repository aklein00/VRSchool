# Goblin music teacher — editable character

Built in Blender 4.5.10 from the current individual goblin sketch, with the olive, cream, terracotta and brown palette of the newer music-lesson illustration. Original references are included in `reference/` and hidden inside the Blender file. The back and obscured forms are a 3D interpretation; the reference is a single view, not an orthographic turnaround.

## Open these files

- **Goblin_Music_Teacher.blend** — complete assembled character, 130 separately editable mesh objects, named collections, UV0, packed painted textures, lighting and portrait camera. The pose is a relaxed A-pose. Objects have individual local origins; no armature is included.
- **gimp/*_Paint.xcf** — ten native GIMP documents, saved and reopened in GIMP 3.0.8. Each contains eight editable layers. The corresponding OpenRaster files are also available as interchange backups.
- **textures/** — matching BaseColor and Roughness PNGs. BaseColor is sRGB; Roughness is Non-Color. Geometry supplies the surface detail; no normal map is required.
- **uv-layouts/** — transparent PNG and vector SVG wireframes for every texture set.
- **exports/Goblin_Music_Teacher.fbx** and **.glb** — assembled exports with separate named meshes and embedded textures. `exports/parts/` contains one FBX for each of the ten part categories, preserving their component meshes and assembly positions.
- **previews/** — actual Blender renders: painted portrait, face detail, front, back and a UV checker inspection.

## Mesh organization

Head/neck/ears and facial contours; upper body coat panels, lapels, sleeves, cuffs, waistcoat and scarf; separate breeches and stockings; left/right shoe uppers, soles and cuffs; left/right hands with five fingers; left/right eyes containing globe, iris and pupil geometry; separate fangs; hair cap and locks; independent eyebrows; earrings, buttons, strap, belt tab and lute parts. Some small details are disconnected mesh islands inside a named assembly, such as the nails in each hand and the strings of the lute.

The model is **1.474 meters tall**, including the hair/ears, with **108,874 triangles**. This is a static editable art model. It has no rig, skin weights, facial blend shapes, animation, LODs or collision meshes. Sculpt-derived and generated surfaces have not been validated for deformation. Headset performance has not been tested; production animation/VR use needs its own topology, LOD, material consolidation and rigging pass.

## Texel density

Density is measured from the actual triangle surface area and UV area at the supplied model scale, rather than inferred from image dimensions. Islands are packed without intentional mirrored or stacked UVs. The per-object measurements are in `asset-manifest.json` and `parts-and-texel-density.csv`. Targets below are atlas-wide RMS densities; individual islands can vary due to projection distortion.

| Texture set | Resolution | Pixels/meter | UV coverage |
| --- | --- | ---: | ---: |
| 01_Face | 4096 × 4096 | 2,048 | 17.3% |
| 02_Hands | 1024 × 1024 | 2,048 | 30.1% |
| 03_Upper | 4096 × 4096 | 1,024 | 11.6% |
| 04_Scarf | 1024 × 1024 | 1,536 | 42.1% |
| 05_Lower | 2048 × 2048 | 1,024 | 16.3% |
| 06_Shoes | 2048 × 2048 | 1,536 | 19.4% |
| 07_Hair | 4096 × 4096 | 1,536 | 9.0% |
| 08_EyesTeeth | 2048 × 2048 | 4,096 | 12.4% |
| 09_Accessories | 2048 × 2048 | 2,048 | 15.3% |
| 10_Lute | 2048 × 2048 | 2,048 | 22.3% |

Face and hands receive more detail than the main clothing, while small eye and tooth features receive the highest density. Texture sets are shared by related separate objects to keep repainting manageable. Color extends up to eight pixels into empty UV gutters, limited by nearest-island ownership. These are editable source-resolution textures; reduce or consolidate them separately when establishing the runtime memory budget.

## Repaint in GIMP

1. Open the matching `gimp/NN_Name_Paint.xcf` file. Turn on **UV guide - HIDDEN for export** only while locating a surface.
2. Paint on **Your paint edits**, or change the base palette, cool form shadows, broad pigment washes, warm edge highlights, warm facial accents and selective brush strokes independently.
3. Hide the UV guide before export. Save the XCF to retain all layers, then export over the matching `textures/NN_Name_BaseColor.png` at its original resolution. Saving the XCF alone does not update Blender.
4. In Blender, open the Text Editor, choose **RELOAD_PAINTED_TEXTURES.py** from the text dropdown, and click **Run Script**. This reloads the external PNGs and repacks them. Save the Blender file afterward. The same helper is in `source/reload_painted_textures.py`.
5. Re-export FBX/GLB after repainting if you need the interchange files updated too. Existing exports do not refresh automatically.

The finish is **procedurally authored in a hand-painted style**: deliberate pigment colors, broad form shading, warm highlights and selective directional marks. It is not a projection of the sketch or a claim of manual brush painting. Layers are raster paint surfaces and remain editable in GIMP.

## Validation and rebuild

`validation-report.json` records mesh/UV/packed-image checks and fresh FBX/GLB import checks. `source/gimp-validation.json` records the native XCF reopen checks and layer names. `source/texture-validation.json` records rasterized UV overlap measurements. Review the checker image alongside the measurements when making later UV edits.

Construction, UV, texture authoring, GIMP-save and export scripts are included in `source/`. To rebuild into a duplicate folder, run `build_character.py` and `unwrap_character.py` in Blender, `paint_textures.py` in Python with NumPy/Pillow/SciPy, `save_gimp.py` through GIMP's Python batch interpreter with its `__file__` set, then `finalize_character.py` in Blender. Scripts overwrite their generated outputs; keep your repainted XCF/PNG files in a separate copy before rebuilding.

Native GIMP API references: [save](https://developer.gimp.org/api/3.0/libgimp/func.file_save.html) and [load](https://developer.gimp.org/api/3.0/libgimp/func.file_load.html).
