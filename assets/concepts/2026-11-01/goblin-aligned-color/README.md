# Goblin music teacher — aligned color references

Three separate 1024 × 1024 RGB PNG files: `front.png`, `left_side.png`, and `back.png`. Use these individual images for generation. The ZIP contains only these three files; `preview.png` is a visual comparison, not a generation input.

The original pencil turnaround was edited using the built-in image-generation tool. The colored front view then served as the palette and identity reference for the side and back. No rejected 3D model was used. Generated originals are retained in `source/`.

All three images use a pure white background without titles, view labels, a ground line or a cast ground shadow. Colors are broad local colors with restrained form shading: olive skin and coat, salmon ear interiors, chestnut hair, ivory waistcoat/cuffs, rust scarf, brown breeches, charcoal stockings, cognac boots and brass fittings.

## Alignment

The requested canvas isolation and landmark registration were finished deterministically after generation. Anatomical landmarks were placed manually on each original, then mapped to shared pixel rows with a monotonic vertical adjustment and a uniform horizontal scale. Original artwork was preserved during this layout operation; no extra geometry or props were painted in.

Pixel coordinates start at the top-left corner:

| Landmark | Shared Y row |
| --- | ---: |
| Highest ear tip | 100 |
| Shoulder/upper sleeve attachment | 360 |
| Waist/belt level (covered by coat on back) | 550 |
| Bottom of knee cuff | 768 |
| Top of boot cuff | 830 |
| Bottom of boot sole | 944 |

`alignment.json` records original landmarks and final canvas rows. These are registered concept illustrations; matching these rows does not make the drawings metrically exact 3D projections or guarantee a particular generator's result.

The exact generation prompt set is saved in `generation-prompts.json`.
