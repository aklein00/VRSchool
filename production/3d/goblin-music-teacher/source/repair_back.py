import bpy,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for file in ['Goblin_Model_Source.blend','Goblin_UV_Source.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source'/file))
    if 'Coat back' in bpy.data.objects:continue
    rings=[(.79,.207,.172),(.88,.228,.18),(1.02,.225,.174),(1.12,.209,.158),(1.19,.118,.106)]
    vv=[];ff=[];bn=24;S=.82
    for z,rx,ry in rings:
        for j in range(bn+1):
            a=math.pi*j/bn;vv.append((S*rx*math.cos(a),S*(.03+ry*math.sin(a)),S*z))
    for i in range(len(rings)-1):
        for j in range(bn):
            a=i*(bn+1)+j;ff.append((a,a+1,a+bn+2,a+bn+1))
    mesh=bpy.data.meshes.new('Coat back');mesh.from_pydata(vv,[],ff);mesh.update()
    o=bpy.data.objects.new('Coat back',mesh);bpy.data.collections['02 Upper body'].objects.link(o);mesh.materials.append(bpy.data.materials['Coat olive wool'])
    bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Shaping','SUBSURF');mod.levels=2;bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=o.modifiers.new('Tailored thickness','SOLIDIFY');mod.thickness=.018*S;bpy.ops.object.modifier_apply(modifier=mod.name)
    for p in mesh.polygons:p.use_smooth=True
    o['part_category']='02 Upper body';o['texture_style']='Authored painterly color, broad form shading, selective directional strokes'
    for obj in bpy.data.objects:
        if obj.name.startswith('Coat tail.'):
            for v in obj.data.vertices:v.co.y+=.10*S
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/file))
print('BACK_REPAIRED',flush=True)
