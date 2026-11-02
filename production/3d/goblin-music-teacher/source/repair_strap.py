import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name in ['Goblin_Model_Source.blend','Goblin_UV_Source.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source'/name))
    o=bpy.data.objects['Lute shoulder strap']
    if o.get('rear_clearance'):continue
    for v in o.data.vertices:
        if v.co.y>0:v.co.y+=.075*.82*min(1,v.co.y/(.05*.82))
    o['rear_clearance']=True
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/name))
