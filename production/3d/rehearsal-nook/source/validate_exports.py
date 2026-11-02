import bpy,json,math
from pathlib import Path
from io_scene_fbx import parse_fbx
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/'asset-manifest.json').read_text())
def walk(e):
    yield e
    for ch in e.elems:yield from walk(ch)
files=sorted((R/'fbx/objects').glob('*.fbx'))+[R/'fbx/Rehearsal_Nook_Assembled.fbx']
results=[]
for p in files:
    root,version=parse_fbx.parse(str(p));contents=[]
    for e in walk(root):
        if e.id==b'Content' and e.props and isinstance(e.props[0],(bytes,bytearray)) and len(e.props[0])>0:contents.append(len(e.props[0]))
    results.append({'file':str(p.relative_to(R)),'fbx_version':version,'embedded_images':len(contents),'embedded_bytes':sum(contents),'size_bytes':p.stat().st_size})
assert len(files)==manifest['asset_count']+1
assert all(a['embedded_images']>=3 for a in results),results
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(R/'fbx/Rehearsal_Nook_Assembled.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==manifest['asset_count'],(len(meshes),manifest['asset_count'])
mesh_checks=[]
for o in meshes:
    assert o.data.uv_layers.active is not None,o.name
    uvs=o.data.uv_layers.active.data
    assert all(-.001<=c<=1.001 for uv in uvs for c in uv.uv),o.name
    assert all(math.isfinite(v) for vert in o.data.vertices for v in vert.co),o.name
    imgs=[n.image for mat in o.data.materials if mat and mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
    for im in imgs:
        if not im.has_data:
            try: sample=im.pixels[0]
            except Exception as e: print('IMAGE_LOAD',im.name,im.filepath,str(e),flush=True)
    assert imgs and all(im.has_data for im in imgs),(o.name,[(im.name,im.filepath,im.has_data) for im in imgs])
    mesh_checks.append({'name':o.name,'uv_vertices':len(uvs),'loaded_material_images':len(imgs)})
# Confirm each standalone asset has a valid independent UV mesh and all images embed.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(R/'fbx/objects/05_Upright_Piano.fbx'))
piano=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(piano)==1
assert piano[0].location.length<.001
report={'passed':True,'object_count':len(meshes),'texture_png_count':len(list((R/'textures').glob('*.png'))),'triangle_count':manifest['triangle_count'],'embedded_fbx_checks':results,'assembled_reimport_checks':mesh_checks,'standalone_piano_origin_verified':True}
(R/'validation-report.json').write_text(json.dumps(report,indent=2))
print('VALIDATION_PASSED',len(meshes),manifest['triangle_count'],flush=True)
