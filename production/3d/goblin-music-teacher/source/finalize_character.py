import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source/Goblin_UV_Source.blend'))
manifest=json.loads((ROOT/'asset-manifest.json').read_text())
objs=[bpy.data.objects[o['name']] for o in manifest['objects']]
materials={}
for g,a in manifest['atlases'].items():
    m=bpy.data.materials.new(g+' | editable painted texture');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
    out=n.new('ShaderNodeOutputMaterial');out.location=(560,0)
    bs=n.new('ShaderNodeBsdfPrincipled');bs.location=(280,0);bs.inputs['Specular IOR Level'].default_value=.24
    l.new(bs.outputs['BSDF'],out.inputs['Surface'])
    uv=n.new('ShaderNodeUVMap');uv.uv_map='UV0';uv.location=(-550,0)
    for kind,y in [('BaseColor',100),('Roughness',-150)]:
        tex=n.new('ShaderNodeTexImage');tex.location=(-280,y);im=bpy.data.images.load(str(ROOT/'textures'/f'{g}_{kind}.png'),check_existing=True)
        im.colorspace_settings.name='sRGB' if kind=='BaseColor' else 'Non-Color';tex.image=im;tex.label=kind+' - repaint in '+g+'_Paint.xcf'
        l.new(uv.outputs['UV'],tex.inputs['Vector']);l.new(tex.outputs['Color'],bs.inputs['Base Color' if kind=='BaseColor' else 'Roughness'])
        if kind=='BaseColor':n.active=tex
    m['editable_source']='gimp/'+g+'_Paint.xcf';materials[g]=m
for o in objs:
    g=o['atlas'];o.data.materials.clear();o.data.materials.append(materials[g])
    for p in o.data.polygons:p.material_index=0
    # Center local origins on each component while retaining the assembled world-space pose.
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
scene=bpy.context.scene
scene.cycles.samples=48
scene.render.resolution_x=1400;scene.render.resolution_y=1600
scene.view_settings.view_transform='AgX'
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.18,.21,.25,1);scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.35
floor=bpy.data.objects['Studio floor'];floor.location.z=.023
f=floor.data.materials[0];f.use_nodes=True;f.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.20,.225,.21,1)
cam=scene.camera
def aim(p,look,scale):cam.location=p;cam.rotation_euler=(Vector(look)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
aim((1.7,-5,1.9),(0,0,.77),1.72)
# Keep concept references available inside the source file in a disabled collection.
c=bpy.data.collections.new('REFERENCE | original sketch and palette');scene.collection.children.link(c)
for name,file,x in [('Approved sketch','10-music-goblin.png',-1.2),('Color direction','01-goblin-music-lesson.png',1.4)]:
    p=ROOT/'reference'/file
    if p.exists():
        im=bpy.data.images.load(str(p));e=bpy.data.objects.new(name,None);e.empty_display_type='IMAGE';e.data=im;e.empty_display_size=1.5;e.location=(x,.3,.8);e.rotation_euler=(math.pi/2,0,0);e.hide_render=True;c.objects.link(e)
c.hide_viewport=True;c.hide_render=True
for o in bpy.data.objects:
    if o.type=='MESH' and o not in objs:o.hide_select=True
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=next(o for o in objs if o.name.startswith('Head |'))
# Portable exports retain all distinct objects and their names.
(ROOT/'exports/parts').mkdir(exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'exports/Goblin_Music_Teacher.glb'),export_format='GLB',use_selection=True,export_apply=True)
bpy.ops.export_scene.fbx(filepath=str(ROOT/'exports/Goblin_Music_Teacher.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,path_mode='COPY',embed_textures=True,axis_forward='-Z',axis_up='Y')
for cat in sorted({o['part_category'] for o in objs}):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        if o['part_category']==cat:o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(ROOT/'exports/parts'/f'{cat.replace(" ","_")}.fbx'),use_selection=True,object_types={'MESH'},add_leaf_bones=False,path_mode='COPY',embed_textures=True,axis_forward='-Z',axis_up='Y')
for im in bpy.data.images:
    if im.source=='FILE':
        im.pack();im.filepath=bpy.path.relpath(im.filepath,start=str(ROOT))
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=next(o for o in objs if o.name.startswith('Head |'));bpy.context.view_layer.objects.active.select_set(True)
reload_script='''# Run this after exporting edited BaseColor PNGs from GIMP. Then save the Blender file.
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
'''
text=bpy.data.texts.new('RELOAD_PAINTED_TEXTURES.py');text.write(reload_script)
(ROOT/'source/reload_painted_textures.py').write_text(reload_script)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Goblin_Music_Teacher.blend'),relative_remap=False)
scene.render.filepath=str(ROOT/'previews/02_painted_character.png');bpy.ops.render.render(write_still=True)
scene.cycles.samples=32
scene.render.resolution_x=1200;scene.render.resolution_y=1200
aim((.9,-4,1.5),(0,0,1.17),.88);scene.render.filepath=str(ROOT/'previews/03_face_detail.png');bpy.ops.render.render(write_still=True)
scene.render.resolution_x=1000;scene.render.resolution_y=1200
for name,p in [('04_front',(0,-5,1.05)),('05_back',(1.6,5,1.6))]:
    aim(p,(0,0,.75),1.72);scene.render.filepath=str(ROOT/'previews'/f'{name}.png');bpy.ops.render.render(write_still=True)
for g,a in manifest['atlases'].items():
    m=materials[g];n=m.node_tree.nodes;bs=next(t for t in n if t.type=='BSDF_PRINCIPLED');uv=next(t for t in n if t.type=='UVMAP')
    checker=n.new('ShaderNodeTexChecker');checker.inputs['Color1'].default_value=(.03,.07,.09,1);checker.inputs['Color2'].default_value=(.65,.75,.69,1);checker.inputs['Scale'].default_value=a['resolution']/64
    m.node_tree.links.new(uv.outputs['UV'],checker.inputs['Vector']);m.node_tree.links.new(checker.outputs['Color'],bs.inputs['Base Color'])
aim((1.7,-5,1.9),(0,0,.77),1.72);scene.render.filepath=str(ROOT/'previews/06_UV_checker.png');bpy.ops.render.render(write_still=True)
print('FINAL_COMPLETE',flush=True)
