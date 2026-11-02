import bpy,json,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
prefixes=('Lapel piping.','Sleeve seam.','Trouser seam.')
for filename in ['Goblin_Model_Source.blend','Goblin_UV_Source.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source'/filename))
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes):bpy.data.objects.remove(o,do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source'/filename))
d=json.loads((ROOT/'asset-manifest.json').read_text());d['objects']=[o for o in d['objects'] if not o['name'].startswith(prefixes)]
d['total_triangles']=sum(o['triangles'] for o in d['objects'])
for g in ['03_Upper','05_Lower']:
    a=d['atlases'][g];a['objects']=[n for n in a['objects'] if not n.startswith(prefixes)]
    a['surface_m2']=sum(o['surface_m2'] for o in d['objects'] if o['atlas']==g)
    a['uv_coverage_percent']=100*sum(o['uv_area'] for o in d['objects'] if o['atlas']==g)
    p=ROOT/'source'/f'{g}_surface.npz';data=np.load(p);t=data['triangles'];names=data['names'];keep=[i for i,n in enumerate(names) if not n.startswith(prefixes)]
    t=t[np.isin(t[:,0,-1],keep)];old=t[:,:,12].copy()
    for new,index in enumerate(keep):t[:,:,12][old==index]=new
    np.savez_compressed(p,triangles=t,names=names[keep],resolution=int(data['resolution']))
    polygons=[]
    for name in a['objects']:
        o=bpy.data.objects[name];uv=o.data.uv_layers.active.data
        for f in o.data.polygons:polygons.append([[float(uv[i].uv.x),float(uv[i].uv.y)] for i in f.loop_indices])
    (ROOT/'uv-layouts'/f'{g}_polygons.json').write_text(json.dumps(polygons,separators=(',',':')))
    n=a['resolution'];svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{n}" height="{n}" viewBox="0 0 {n} {n}"><g fill="none" stroke="#79b4c3" stroke-width="0.6" opacity="0.7">']
    for p in polygons:svg.append('<polygon points="'+' '.join(f'{x*n:.2f},{(1-y)*n:.2f}' for x,y in p)+'"/>')
    svg.append('</g></svg>');(ROOT/'uv-layouts'/f'{g}_UV.svg').write_text('\n'.join(svg))
(ROOT/'asset-manifest.json').write_text(json.dumps(d,indent=2))
print('TRIM_CLEANUP',len(d['objects']),d['total_triangles'],flush=True)
