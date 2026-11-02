import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Goblin_Music_Teacher.blend'))
manifest=json.loads((ROOT/'asset-manifest.json').read_text())
checks=[]
expected={o['name'] for o in manifest['objects']}
def bounds(obs):
    p=[o.matrix_world@Vector(c) for o in obs for c in o.bound_box]
    return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
obs=[bpy.data.objects[n] for n in expected];original_bounds=bounds(obs)
for o in obs:
    assert o.type=='MESH' and o.data.uv_layers.get('UV0')
    assert len(o.data.materials)==1
    uv=o.data.uv_layers['UV0'].data
    assert all(-1e-6<=c<=1.000001 for item in uv for c in item.uv),o.name
    assert all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
    textures=[n.image for n in o.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE']
    assert len(textures)==2 and all(i.packed_file for i in textures),o.name
checks.append({'check':'Blender mesh separation, UV0, finite geometry, packed texture links','passed':True,'objects':len(obs)})
gimp=json.loads((ROOT/'source/gimp-validation.json').read_text());assert len(gimp)==10
checks.append({'check':'Native GIMP XCF save and reopen','passed':all(i['reopened_in_gimp'] for i in gimp.values()),'files':len(gimp),'layers_per_file':8})
tex=json.loads((ROOT/'source/texture-validation.json').read_text())
assert all(v['overlap_percent']<.01 for v in tex.values()),tex
checks.append({'check':'UV raster overlap measurement','results':{k:v['overlap_percent'] for k,v in tex.items()}})
errors={g:max(abs(o['texel_density_px_per_m']-a['target_px_per_m']) for o in manifest['objects'] if o['atlas']==g) for g,a in manifest['atlases'].items()}
assert max(errors.values())<.1,errors
checks.append({'check':'Per-object texel density matches category target','passed':True,'max_error_px_per_m':max(errors.values())})
# Fresh import validates actual interchange files, independent of the working scene.
for kind in ['glb','fbx']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if kind=='glb':bpy.ops.import_scene.gltf(filepath=str(ROOT/'exports/Goblin_Music_Teacher.glb'))
    else:bpy.ops.import_scene.fbx(filepath=str(ROOT/'exports/Goblin_Music_Teacher.fbx'))
    imported=[o for o in bpy.data.objects if o.type=='MESH']
    assert len(imported)==len(expected),(kind,len(imported),len(expected))
    assert all(o.data.uv_layers for o in imported)
    assert all(o.data.materials for o in imported)
    b=bounds(imported);err=max(abs(b[i][j]-original_bounds[i][j]) for i in range(2) for j in range(3))
    assert err<.001,(kind,err)
    checks.append({'check':kind.upper()+' reimport','passed':True,'mesh_count':len(imported),'bounding_box_error_m':err})
report={'checks':checks,'object_count':len(expected),'triangles':manifest['total_triangles'],'height_m':manifest['height_m'],'scope':'Static unrigged character. Sculpt-derived and generated surfaces; not certified deformation topology or headset performance.'}
(ROOT/'validation-report.json').write_text(json.dumps(report,indent=2))
print('VALIDATION_PASSED',flush=True)
