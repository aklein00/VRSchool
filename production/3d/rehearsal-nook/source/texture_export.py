import bpy, os, math, json, time, numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
# Final placement corrections and richer, quieter painted palette.
bpy.data.objects['27_Window_Plant'].location.z += .22
bpy.data.objects['21_Book_Group_4'].location.z += .25
for mat in bpy.data.materials:
    if mat.use_nodes:
        for n in mat.node_tree.nodes:
            if n.type=='VALTORGB':
                for el in n.color_ramp.elements:el.color=tuple(max(0,v)**1.25 for v in el.color[:3])+(1,)
# Named collections keep semantic assets easy to isolate in the Blender file.
for o in list(scene.objects):
    if 'texture_resolution' not in o:continue
    number=int(o.name.split('_')[0]);name='Architecture' if number<=4 else ('Piano and seating' if number<=15 else ('Instruments and props' if number<=25 else 'Plants and wall dressing'))
    coll=bpy.data.collections.get(name)
    if coll is None:coll=bpy.data.collections.new(name);scene.collection.children.link(coll)
    for old in list(o.users_collection):old.objects.unlink(o)
    coll.objects.link(o)
assets=sorted([o for o in scene.objects if o.type=='MESH' and 'texture_resolution' in o],key=lambda o:o.name)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True
scene.render.bake.margin=12;scene.render.bake.use_clear=True
records=[]
def scalar_maps(o,res):
    vals=np.zeros((res,res,4),dtype=np.float32);vals[:,:,0]=.68;vals[:,:,1]=0;vals[:,:,3]=1
    o.data.calc_loop_triangles();uv=o.data.uv_layers.active.data
    for tr in o.data.loop_triangles:
        mat=o.data.materials[tr.material_index];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        rough=bs.inputs['Roughness'].default_value;metal=bs.inputs['Metallic'].default_value
        if abs(rough-.68)<.001 and metal==0:continue
        pts=np.array([uv[i].uv[:] for i in tr.loops])*res
        x0=max(0,int(np.floor(pts[:,0].min()))-2);x1=min(res,int(np.ceil(pts[:,0].max()))+2)
        y0=max(0,int(np.floor(pts[:,1].min()))-2);y1=min(res,int(np.ceil(pts[:,1].max()))+2)
        if x1<=x0 or y1<=y0:continue
        xx,yy=np.meshgrid(np.arange(x0,x1)+.5,np.arange(y0,y1)+.5)
        a,b,c=pts;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-8:continue
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        mask=(u>=-.05)&(v>=-.05)&((u+v)<=1.05)
        sub=vals[y0:y1,x0:x1];sub[:,:,0][mask]=rough;sub[:,:,1][mask]=metal
    maps=[]
    for channel,label in [(0,'Roughness'),(1,'Metallic')]:
        pix=np.ones((res,res,4),dtype=np.float32);pix[:,:,:3]=vals[:,:,channel,None]
        im=bpy.data.images.new(o.name+'_'+label,width=res,height=res,alpha=False);im.colorspace_settings.name='Non-Color';im.pixels.foreach_set(pix.ravel());im.filepath_raw=str(R/'textures'/f'{o.name}_{label}.png');im.file_format='PNG';im.save();maps.append(im)
    return maps
for idx,o in enumerate(assets):
    start=time.time();res=int(o['texture_resolution'])
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    im=bpy.data.images.new(o.name+'_BaseColor',width=res,height=res,alpha=False);im.filepath_raw=str(R/'textures'/f'{o.name}_BaseColor.png');im.file_format='PNG'
    for mat in o.data.materials:
        nodes=mat.node_tree.nodes
        for node in nodes:node.select=False
        tx=nodes.new('ShaderNodeTexImage');tx.image=im;tx.select=True;nodes.active=tx
    bpy.ops.object.bake(type='DIFFUSE');im.save()
    rough,metal=scalar_maps(o,res)
    mat=bpy.data.materials.new(o.name+'_Painted');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF')
    for image,socket in [(im,'Base Color'),(rough,'Roughness'),(metal,'Metallic')]:
        tx=n.new('ShaderNodeTexImage');tx.image=image;tx.label=socket;l.new(tx.outputs['Color'],bs.inputs[socket])
    o.data.materials.clear();o.data.materials.append(mat)
    for p in o.data.polygons:p.material_index=0
    # A vector UV layout for each separate asset, useful for repainting.
    uv=o.data.uv_layers.active.data;lines=[]
    for poly in o.data.polygons:
        pts=['%.2f,%.2f'%(uv[i].uv.x*1024,(1-uv[i].uv.y)*1024) for i in poly.loop_indices]
        lines.append('<polygon points="'+' '.join(pts)+'"/>')
    (R/'uv-layouts'/f'{o.name}_UV.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024"><rect width="1024" height="1024" fill="white"/><g fill="none" stroke="#272230" stroke-width="0.5">'+''.join(lines)+'</g></svg>')
    o.data.calc_loop_triangles()
    records.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'uv_map':'UV0','texture_size':res,'materials':1,'location_m':list(o.location),'textures':[Path(a.filepath_raw).name for a in [im,rough,metal]]})
    print('BAKED',idx+1,'/',len(assets),o.name,round(time.time()-start,1),flush=True)
# Save final scene with images packed and relative on-disk paths.
# Keep absolute paths until the main blend is saved at its delivery location.
scene.cycles.samples=48
scene.render.filepath=str(R/'previews/02_final_beauty.png')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Rehearsal_Nook.blend'))
bpy.ops.file.make_paths_relative()
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Rehearsal_Nook.blend'))
# Separate FBX files use local ground-center pivots. Assembled FBX preserves scene placements.
for o in assets:
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    pos=o.location.copy();o.location=(0,0,0)
    bpy.ops.export_scene.fbx(filepath=str(R/'fbx/objects'/f'{o.name}.fbx'),use_selection=True,object_types={'MESH'},path_mode='COPY',embed_textures=True,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,use_mesh_modifiers=True,mesh_smooth_type='FACE',bake_anim=False)
    o.location=pos
bpy.ops.object.select_all(action='DESELECT')
for o in assets:o.select_set(True)
bpy.context.view_layer.objects.active=assets[0]
bpy.ops.export_scene.fbx(filepath=str(R/'fbx/Rehearsal_Nook_Assembled.fbx'),use_selection=True,object_types={'MESH'},path_mode='COPY',embed_textures=True,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,use_mesh_modifiers=True,mesh_smooth_type='FACE',bake_anim=False)
bpy.ops.export_scene.gltf(filepath=str(R/'sketchfab/Rehearsal_Nook_Assembled.glb'),export_format='GLB',use_selection=True,export_apply=True)
manifest={'title':'Alpine Rehearsal Nook','units':'meters','asset_count':len(assets),'triangle_count':sum(a['triangles'] for a in records),'assets':records,'texture_notes':'Per-object UV0 base-color maps baked from broad low-frequency color washes; brighter material on actual bevel faces is baked into base color. Separate non-color roughness and metallic maps. No painted texture noise or normal map is needed for the modeled edge bevels.','lighting':[]}
for o in scene.objects:
    if o.type=='LIGHT':manifest['lighting'].append({'name':o.name,'type':o.data.type,'location':list(o.location),'rotation_radians':list(o.rotation_euler),'energy':o.data.energy,'color_linear':list(o.data.color),'size':getattr(o.data,'size',None)})
(R/'asset-manifest.json').write_text(json.dumps(manifest,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Rehearsal_Nook.blend'))
bpy.ops.render.render(write_still=True)
# Alternate viewing angle to verify geometry outside the hero camera.
cam=scene.camera;loc=cam.location.copy();rot=cam.rotation_euler.copy()
from mathutils import Vector
cam.location=(7,-10,12);cam.rotation_euler=(Vector((0,.2,1.35))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.cycles.samples=24;scene.render.filepath=str(R/'previews/03_layout_overview.png');bpy.ops.render.render(write_still=True)
cam.location=loc;cam.rotation_euler=rot
print('EXPORT_COMPLETE',flush=True)
