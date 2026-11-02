# Run this after exporting edited BaseColor PNGs from GIMP. Then save the Blender file.
import bpy
from pathlib import Path
folder=Path(bpy.data.filepath).parent / 'textures'
for image in bpy.data.images:
    path=folder / Path(image.filepath).name
    if path.exists():
        if image.packed_file:
            image.unpack(method='REMOVE')
        image.filepath=str(path)
        image.reload()
        image.pack()
        image.filepath='//textures/'+path.name
print('Painted textures reloaded and packed. Save the Blender file to keep changes.')
