import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=bpy.context.scene
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active=bpy.data.objects['05_Upright_Piano']
s.render.filepath='//previews/02_final_beauty.png'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='MATERIAL'
            area.spaces.active.overlay.show_overlays=False
s['Delivery']='37 independent UV-mapped assets; embedded-texture FBX exports; separate PNG maps.'
s['Source concept']='04-rehearsal-nook-diorama-v4.png'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Rehearsal_Nook.blend'))
print('FINAL_SCENE_SAVED')
