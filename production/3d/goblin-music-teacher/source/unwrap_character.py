import bpy, math,json,os
import numpy as np
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ONLY=os.environ.get('VRHS_ATLAS')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/('source/Goblin_UV_Source.blend' if ONLY else 'source/Goblin_Model_Source.blend')))
objects=[o for o in bpy.data.objects if o.type=='MESH' and 'STUDIO' not in [c.name for c in o.users_collection]]
groups={}
for o in objects:
    keys={m.get('atlas') for m in o.data.materials}
    assert len(keys)==1,(o.name,keys)
    groups.setdefault(keys.pop(),[]).append(o)
targets={'01_Face':2048,'02_Hands':2048,'03_Upper':1024,'04_Scarf':1536,'05_Lower':1024,'06_Shoes':1536,'07_Hair':1536,'08_EyesTeeth':4096,'09_Accessories':2048,'10_Lute':2048}
report={'height_m':0,'atlases':{},'objects':[]}
if ONLY:
    report=json.loads((ROOT/'asset-manifest.json').read_text());report['objects']=[o for o in report['objects'] if o['atlas']!=ONLY]
z=[v.co.z for o in objects for v in o.data.vertices];report['height_m']=max(z)-min(z)
for g,obs in sorted(groups.items()):
    if ONLY and ONLY!=g:continue
    print('UNWRAP',g,len(obs),flush=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(48),island_margin=.015,area_weight=.3,correct_aspect=True,scale_to_bounds=False)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.average_islands_scale()
    bpy.ops.object.mode_set(mode='OBJECT')
    # Multi-object average-islands can retain different per-object normalization.
    # Normalize each object's total UV area to its true surface area before the joint pack.
    for o in obs:
        o.data.calc_loop_triangles();uv=o.data.uv_layers.active.data;oa=ou=0
        for t in o.data.loop_triangles:
            q=[uv[i].uv for i in t.loops];oa+=t.area;ou+=abs((q[1]-q[0]).cross(q[2]-q[0]))*.5
        factor=math.sqrt(oa/ou)
        for item in uv:item.uv*=factor
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True,margin=.004,shape_method='CONCAVE',margin_method='FRACTION')
    bpy.ops.object.mode_set(mode='OBJECT')
    A=U=0
    for o in obs:
        o.data.calc_loop_triangles();uv=o.data.uv_layers.active.data
        for t in o.data.loop_triangles:
            q=[uv[i].uv for i in t.loops];u=abs((q[1]-q[0]).cross(q[2]-q[0]))*.5
            A+=t.area;U+=u
    target=targets[g];res=256
    while res*math.sqrt(U/A)<target*1.02:res*=2
    factor=target/(res*math.sqrt(U/A))
    for o in obs:
        o.data.uv_layers.active.name='UV0'
        for uv in o.data.uv_layers.active.data:uv.uv=(uv.uv-Vector((.5,.5)))*factor+Vector((.5,.5))
    tris=[];names=[];layout=[]
    for oi,o in enumerate(obs):
        uv=o.data.uv_layers.active.data;a=u=0
        for t in o.data.loop_triangles:
            q=[uv[i].uv for i in t.loops];u+=abs((q[1]-q[0]).cross(q[2]-q[0]))*.5;a+=t.area
            ma=o.data.materials[t.material_index];col=ma['paint_rgb'];rough=ma.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value
            row=[]
            for li,vi in zip(t.loops,t.vertices):
                row.append([*uv[li].uv,*o.data.vertices[vi].co,*o.data.corner_normals[li].vector,*col,rough,float(oi)])
            tris.append(row)
        names.append(o.name)
        for p in o.data.polygons:layout.append([[float(uv[i].uv.x),float(uv[i].uv.y)] for i in p.loop_indices])
        info={'name':o.name,'category':o['part_category'],'atlas':g,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'surface_m2':a,'uv_area':u,'texel_density_px_per_m':res*math.sqrt(u/a) if a else 0}
        o['atlas']=g;o['texel_density_px_per_m']=info['texel_density_px_per_m'];o['texture_resolution']=res
        report['objects'].append(info)
    np.savez_compressed(ROOT/'source'/f'{g}_surface.npz',triangles=np.asarray(tris,dtype=np.float32),names=np.asarray(names),resolution=res)
    (ROOT/'uv-layouts'/f'{g}_polygons.json').write_text(json.dumps(layout,separators=(',',':')))
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{res}" height="{res}" viewBox="0 0 {res} {res}"><g fill="none" stroke="#79b4c3" stroke-width="0.6" opacity="0.7">']
    for p in layout:svg.append('<polygon points="'+' '.join(f'{x*res:.2f},{(1-y)*res:.2f}' for x,y in p)+'"/>')
    svg.append('</g></svg>');(ROOT/'uv-layouts'/f'{g}_UV.svg').write_text('\n'.join(svg))
    report['atlases'][g]={'resolution':res,'target_px_per_m':target,'measured_px_per_m':target,'surface_m2':A,'uv_coverage_percent':100*U*factor*factor,'packing_margin_px':res*.004*factor,'objects':names}
    print('ATLAS',g,res,'px',target,'px/m',flush=True)
report['total_triangles']=sum(o['triangles'] for o in report['objects'])
(ROOT/'asset-manifest.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/Goblin_UV_Source.blend'))
print('UV_COMPLETE',flush=True)
