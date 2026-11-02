import bpy, math, random, os, json, time
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1]
random.seed(23)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.materials): bpy.data.materials.remove(d)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.image_settings.file_format='PNG'
scene.world.color=(.13,.16,.20)
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=-.35
assets=[]; parts=[]; mats={}; material_info={}
PAL={'stone':(.64,.53,.38),'stone_light':(.76,.65,.48),'stone_dark':(.52,.43,.32),'oak':(.31,.14,.045),'oak_light':(.49,.27,.10),'oak_dark':(.17,.073,.025),'gold':(.51,.30,.08),'ivory':(.86,.80,.62),'black':(.018,.022,.025),'sage':(.25,.34,.20),'sage_light':(.39,.46,.27),'plum':(.28,.095,.17),'terracotta':(.47,.18,.10),'blue':(.08,.13,.22),'leaf':(.17,.30,.08),'leaf_light':(.30,.41,.12),'paper':(.89,.82,.64),'ink':(.075,.047,.038),'sky':(.35,.59,.76),'mountain':(.26,.40,.55),'snow':(.76,.85,.88),'soil':(.09,.055,.028)}
def material(key,edge=False):
    k=key+('_edge' if edge else '')
    if k in mats:return mats[k]
    c=PAL[key]; c=tuple(min(.95,x*1.22+.045) for x in c) if edge else c
    m=bpy.data.materials.new(k);m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputMaterial'); bs=n.new('ShaderNodeBsdfPrincipled')
    rough=.36 if key=='gold' else .68
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=.55 if key=='gold' else 0
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3.6;tex.inputs['Detail'].default_value=1;tex.inputs['Roughness'].default_value=.35
    coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Generated'],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[0].color=(*[v*.78 for v in c],1);ramp.color_ramp.elements[1].color=(*[min(1,v*1.12+.005) for v in c],1)
    l.new(tex.outputs['Fac'],ramp.inputs[0])
    sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Generated'],sep.inputs[0])
    grad=n.new('ShaderNodeMapRange');grad.inputs['From Min'].default_value=0;grad.inputs['From Max'].default_value=1;grad.inputs['To Min'].default_value=.72;grad.inputs['To Max'].default_value=1.06;l.new(sep.outputs['Z'],grad.inputs['Value'])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;l.new(ramp.outputs['Color'],mix.inputs[1]);l.new(grad.outputs['Result'],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color']);l.new(bs.outputs[0],out.inputs[0])
    mats[k]=m;material_info[k]={'roughness':rough,'metallic':.55 if key=='gold' else 0}
    return m

def assign(o,key,bev=0):
    o.data.materials.append(material(key))
    if bev:
        o.data.materials.append(material(key,True));m=o.modifiers.new('Painted bevel highlight','BEVEL');m.width=bev;m.segments=2;m.material=1
        m.affect='EDGES'
    parts.append(o);return o

def cube(name,loc,scale,key='oak',bev=.02):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return assign(o,key,bev)
def cyl(name,loc,r,depth,key='oak',verts=16,r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r,radius2=r if r2 is None else r2,depth=depth,location=loc)
    o=bpy.context.object;o.name=name;return assign(o,key,.008 if r>.025 else 0)
def sphere(name,loc,scale,key='oak',seg=16,rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);assign(o,key)
    for p in o.data.polygons:p.use_smooth=True
    return o

def mesh(name,verts,faces,key):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);return assign(o,key)
def rod(name,a,b,r,key='oak',verts=10):
    a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,key,verts);o.rotation_mode='QUATERNION';o.rotation_quaternion=(b-a).to_track_quat('Z','Y');return o

def torus(name,loc,major,minor,key='gold',rot=None):
    bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=6,location=loc,major_radius=major,minor_radius=minor)
    o=bpy.context.object;o.name=name
    if rot:o.rotation_euler=rot
    return assign(o,key)

def path(name,pts,r,key='oak'):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=r;cu.bevel_resolution=1
    sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
    for p,co in zip(sp.points,pts):p.co=(*co,1)
    o=bpy.data.objects.new(name,cu);scene.collection.objects.link(o);o.data.materials.append(material(key));parts.append(o);return o

def finish(name,loc=(0,0,0),rot=0,res=1024):
    global parts
    if not parts:return
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=name
    # Place assembly local coordinates through an origin at zero.
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    o.rotation_euler.z=rot;o.location=loc
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    # Meaningful individual-asset pivot: bottom center of its bounding box.
    verts=[o.matrix_world@Vector(v) for v in o.bound_box]
    scene.cursor.location=((min(v.x for v in verts)+max(v.x for v in verts))/2,(min(v.y for v in verts)+max(v.y for v in verts))/2,min(v.z for v in verts))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    o['texture_resolution']=res;o['asset_type']='independent UV-mapped prop';assets.append(o);parts=[]
    return o

def book(loc=(0,0,0),size=(.3,.22,.07),key='plum',rot=0):
    x,y,z=loc;w,d,h=size
    start=len(parts)
    cube('Pages',(x,y,z+h/2),(w-.02,d-.018,h-.015),'paper',.006)
    for zz in [z+.006,z+h-.006]:cube('Cover',(x,y,zz),(w,d,.012),key,.004)
    cube('Spine',(x-w/2+.008,y,z+h/2),(.018,d,h),key,.005)
    for yy in [-.32,.32]:cube('Spine band',(x-w/2-.004,y+yy*d,z+h/2),(.008,.016,h*.85),'gold',.002)
    if rot:
        from mathutils import Matrix
        mat=Matrix.Translation(Vector(loc))@Matrix.Rotation(rot,4,'Z')@Matrix.Translation(-Vector(loc))
        for ob in parts[start:]:ob.matrix_world=mat@ob.matrix_world

def open_score(loc=(0,0,0),scale=1,tilt=0):
    start=len(parts)
    # flat book centered on origin, fold along Y
    for sign in [-1,1]:
        o=cube('Score cover',(sign*.16,0,.012),(.32,.40,.025),'plum',.008);o.rotation_euler.y=sign*.08
        o=cube('Cream page',(sign*.16,0,.034),(.30,.38,.018),'paper',.004);o.rotation_euler.y=sign*.08
        for row in range(3):
            y=-.11+row*.10
            for line in range(5):
                cube('Staff',(sign*.16,y+line*.010,.052),(.255,.0018,.001),'ink',0)
            for j in range(5):
                xx=sign*.16-.10+j*.043; yy=y+.012+(j%3)*.009
                sphere('Note',(xx,yy,.054),(.007,.004,.0015),'ink',8,4)
    from mathutils import Matrix
    mat=Matrix.Translation(Vector(loc))@Matrix.Rotation(tilt,4,'X')@Matrix.Scale(scale,4)
    for ob in parts[start:]:ob.matrix_world=mat@ob.matrix_world

def pillow(loc,size,key):
    o=cube('Soft cushion',loc,size,key,min(size)*.32)
    o.modifiers[-1].segments=3
    return o

def cloth(name,origin,w,length,key,drop=.65):
    # Cross seat first, then drape down its front, with broad quiet folds.
    nx,ny=16,26;vs=[];fs=[]
    for j in range(ny+1):
        t=j/ny
        yy=origin[1]+.25-t*length*.62
        zz=origin[2]-(max(0,t-.44)/.56)*drop
        for i in range(nx+1):
            u=i/nx;x=origin[0]+(u-.5)*w
            fold=(.014+max(0,t-.4)*.025)*math.sin(u*math.pi*8+t*1.3)
            vs.append((x,yy+fold*.35,zz+fold))
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
    o=mesh(name,vs,fs,key);s=o.modifiers.new('Fabric thickness','SOLIDIFY');s.thickness=.007
    for p in o.data.polygons:p.use_smooth=True
    # Sparse woven border as geometry, no noisy texture.
    for side in [.05,.95]:
        pts=[vs[j*(nx+1)+round(side*nx)] for j in range(ny+1)];path('Woven border',pts,.007,'plum' if key!='plum' else 'terracotta')
    return o

# Architecture: individually modeled floor tiles, chamfered highlighted edges.
cube('Foundation',(0,0,-.12),(6,5,.24),'stone_dark',.055)
for i in range(10):
 for j in range(8):
    cube('Flagstone',(-2.7+i*.6,-2.18+j*.62,.025),(.59,.61,.08),random.choice(['stone','stone','stone_light']),.018)
finish('01_Floor_Base',res=2048)
# Left masonry wall separated from the window wall.
for row in range(8):
    z=.3+row*.47
    bounds=[-2.5]+[v for v in [(-2.5+(.35 if row%2 else .7)+i*.7) for i in range(8)] if -2.5<v<2.5]+[2.5]
    for a,b in zip(bounds[:-1],bounds[1:]):cube('Stone block',(-2.98,(a+b)/2,z),(.24,b-a-.012,.46),random.choice(['stone','stone_light','stone']),.014)
finish('02_Left_Stone_Wall',res=2048)
# Continuous rear wall with actual arched openings, then separate edge stones.
wall=cube('Rear solid', (0,2.46,1.98),(6,.24,3.96),'stone',0)
centers=[-.94,.29,1.52];rad=.52;spring=3.01;bottom=1.63
for c in centers:
    outline=[(c-rad,bottom),(c+rad,bottom),(c+rad,spring)]
    outline += [(c+rad*math.cos(math.pi*i/24),spring+rad*math.sin(math.pi*i/24)) for i in range(1,25)]
    n=len(outline);vs=[(x,y,z) for y in [2.1,2.8] for x,z in outline]
    cutter=mesh('Window cutter',vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'stone')
    import bmesh
    for target in [wall,cutter]:
        bm=bmesh.new();bm.from_mesh(target.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(target.data);bm.free()
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active=wall;mod=wall.modifiers.new('True arched opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
    parts.remove(cutter);bpy.data.objects.remove(cutter,do_unlink=True)
    for i in range(11):
        a=math.pi*i/11+.009;b=math.pi*(i+1)/11-.009;rr=rad+.15;vs=[]
        for yy in [2.26,2.60]:
            vs.extend([(c+rad*math.cos(a),yy,spring+rad*math.sin(a)),(c+rad*math.cos(b),yy,spring+rad*math.sin(b)),(c+rr*math.cos(b),yy,spring+rr*math.sin(b)),(c+rr*math.cos(a),yy,spring+rr*math.sin(a))])
        o=mesh('Arch wedge',vs,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'stone_light');o.data.materials.append(material('stone_light',True));be=o.modifiers.new('Stone edge light','BEVEL');be.width=.01;be.segments=1;be.material=1
for x in [-1.55,-.325,.905,2.135]:
    cyl('Window column',(x,2.29,2.32),.085,1.36,'stone_light',12)
    for z in [1.65,3.00]:cube('Capital',(x,2.29,z),(.23,.31,.12),'stone_light',.022)
cube('Window sill',(.3,2.29,1.62),(3.95,.48,.13),'stone_light',.028)
# Sparse raised coursing on solid wall sides and upper lintel.
for x in [-2.30,2.62]:
 for row in range(8):
    cube('Side facing',(x,2.325,.28+row*.47),(1.30 if x<0 else .69,.035,.45),'stone',.012)
for i in range(8):cube('Top coping',(-2.65+i*.75,2.46,4.0),(.74,.31,.12),'stone_light',.014)
finish('03_Arched_Window_Wall',res=2048)
# Painted mountain view insert behind the real window openings: separable and opaque.
cube('Sky insert',(.28,2.63,2.55),(3.75,.025,2.50),'sky',0)
for layer in range(3):
    xs=[-1.6+i*.34 for i in range(12)]; peaks=[2.05+random.uniform(.0,.85)-layer*.17 for _ in xs]
    vs=[(xs[0],2.60-layer*.008,1.30)]+[(x,2.60-layer*.008,z) for x,z in zip(xs,peaks)]+[(xs[-1],2.60-layer*.008,1.30)]
    mesh('Mountain silhouette',vs,[tuple(range(len(vs)))],['snow','mountain','blue'][layer])
finish('04_Painted_Alpine_View',res=1024)
# Piano in local orientation. Front faces -Y, rotate to face +X in scene.
cube('Piano case',(0,0,.93),(2.05,.52,1.70),'oak',.035)
cube('Top lid',(0,-.015,1.82),(2.17,.62,.09),'oak_light',.02)
cube('Case foot',(0,-.03,.13),(2.13,.64,.13),'oak_dark',.025)
cube('Upper front panel',(0,-.286,1.44),(1.85,.07,.57),'oak_light',.02)
cube('Lower front panel',(0,-.286,.51),(1.84,.07,.58),'oak',.02)
for x in [-.93,.93]:cube('Panel stile',(x,-.34,1.44),(.055,.06,.66),'oak_dark',.012)
for z in [1.11,1.77]:cube('Panel rail',(0,-.34,z),(1.91,.06,.055),'oak_dark',.01)
cube('Keyboard bed',(0,-.52,.99),(2.02,.56,.11),'oak_light',.025)
for x in [-.97,.97]:
 cube('Keyboard cheek',(x,-.52,1.08),(.13,.55,.17),'oak',.025)
 cube('Piano front leg',(x,-.65,.52),(.14,.15,.88),'oak',.018)
 cube('Foot',(x,-.67,.11),(.23,.26,.10),'oak_dark',.025)
for i in range(35):
 x=-.87+i*.0512
 cube('Ivory key',(x,-.59,1.062),(.049,.35,.045),'ivory',.003)
 if i%7 not in [2,6] and i<34:cube('Ebony key',(x+.025,-.49,1.10),(.031,.20,.045),'black',.003)
for x in [-.12,0,.12]:cube('Pedal',(x,-.58,.18),(.055,.24,.035),'gold',.012)
cube('Music rest',(0,-.33,1.28),(1.08,.09,.07),'oak_light',.012)
finish('05_Upright_Piano',(-2.49,.66,.08),math.pi/2,res=2048)
# Piano score separate reusable prop.
open_score((0,0,0),1.05,math.radians(68));finish('06_Piano_Score',(-2.05,.66,1.49),math.pi/2,1024)
# Piano bench local long axis X.
for x in [-.66,.66]:
 for y in [-.20,.20]:
    cube('Bench leg',(x,y,.32),(.10,.10,.57),'oak',.015)
    cube('Bench foot',(x,y,.06),(.14,.14,.10),'oak_dark',.018)
cube('Bench apron',(0,0,.58),(1.48,.53,.14),'oak',.02)
pillow((0,0,.70),(1.51,.57,.15),'plum')
finish('07_Piano_Bench',(-1.48,.66,.08),math.pi/2,1024)
# Window seat.
cube('Seat chest',(.34,1.94,.49),(3.75,.77,.84),'oak_light',.035)
for x in [-.87,.34,1.55]:
 cube('Recessed panel',(x,1.535,.49),(1.07,.035,.57),'oak',.018)
 for dx in [-.55,.55]:cube('Seat stile',(x+dx,1.50,.49),(.055,.045,.68),'oak_light',.008)
cube('Seat lip',(.34,1.91,.95),(3.88,.87,.10),'oak_light',.025)
finish('08_Window_Seat',res=1024)
for i,(x,key) in enumerate([(-.87,'sage'),(.34,'sage_light'),(1.55,'sage')]):
 pillow((x,1.92,1.06),(1.17,.69,.15),key)
 finish('09_Seat_Cushion_'+str(i+1),res=512)
for i,(x,key) in enumerate([(-.75,'sage'),(.05,'ivory'),(.98,'sage')]):
 o=pillow((x,2.13,1.31),(.58,.16,.49),key);o.rotation_euler.x=math.radians(-13);o.rotation_euler.y=math.radians((-1)**i*10)
 finish('10_Back_Cushion_'+str(i+1),res=512)
cloth('Draped plum throw',(1.03,1.80,1.16),.68,1.3,'plum',.70);finish('11_Window_Throw',res=1024)
# Stool
cyl('Stool seat',(0,0,.72),.30,.10,'oak_light',24)
for a in [math.pi/4+i*math.pi/2 for i in range(4)]:
 rod('Splayed stool leg',(.29*math.cos(a),.29*math.sin(a),.08),(.20*math.cos(a),.20*math.sin(a),.69),.045,'oak')
for a in [i*math.pi/2+math.pi/4 for i in range(4)]:
 b=a+math.pi/2;rod('Footrest',(.25*math.cos(a),.25*math.sin(a),.30),(.25*math.cos(b),.25*math.sin(b),.30),.023,'oak_light')
finish('12_Practice_Stool',(.65,-.66,.08),res=1024)
# Stand, broad tripod and bookrest.
for a in [0,2.094,4.189]:rod('Tripod leg',(0,0,.22),(.36*math.cos(a),.36*math.sin(a),.05),.045,'oak')
cyl('Stem',(0,0,.70),.045,1.0,'oak_dark',12)
for z,r in [(.26,.09),(.42,.075),(1.10,.075)]:sphere('Turned collar',(0,0,z),(r,r,.07),'oak_light')
o=cube('Bookrest',(0,0,1.28),(.73,.09,.51),'oak',.02);o.rotation_euler.x=math.radians(-18)
cube('Book ledge',(0,-.125,1.06),(.76,.15,.055),'oak_light',.012)
finish('13_Music_Stand',(-.32,-.12,.08),res=1024)
open_score((0,0,0),1.0,math.radians(72));finish('14_Stand_Score',(-.32,-.20,1.38),res=1024)
# Rug with sewn broad border, no noisy ornamental design.
cube('Rug',(0,-.64,.086),(3.62,2.63,.025),'terracotta',.012)
for x in [-1.73,1.73]:cube('Rug side border',(x,-.64,.102),(.055,2.49,.006),'ivory',.002)
for y in [-1.88,.60]:cube('Rug end border',(0,y,.102),(3.5,.055,.006),'ivory',.002)
finish('15_Rehearsal_Rug',res=1024)
# Cello and lute silhouette meshes. Shape extruded along Y; front points -Y.
def instrument(kind):
    if kind=='cello':
        profile=[(0,.12),(.20,.14),(.32,.25),(.34,.41),(.28,.54),(.15,.60),(.14,.70),(.25,.82),(.25,.95),(.17,1.06),(0,1.10)]
        dep=.12;necktop=1.65
    else:
        profile=[(0,.12),(.19,.15),(.28,.29),(.30,.49),(.24,.68),(.12,.85),(0,.89)];dep=.13;necktop=1.35
    outline=profile+ [(-x,z) for x,z in profile[-2:0:-1]]
    # Catmull-Rom contours give the familiar violin-family curves without tiny detail.
    from mathutils import Vector
    anchors=[Vector(p) for p in outline];smooth=[]
    for ii in range(len(anchors)):
        a,b,c,d=[anchors[(ii+k)%len(anchors)] for k in [-1,0,1,2]]
        for jj in range(4):
            t=jj/4;v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);smooth.append((v.x,v.y))
    outline=smooth
    n=len(outline);vs=[(x,y,z) for y in [-dep,dep] for x,z in outline]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    o=mesh('Instrument body',vs,faces,'oak_light');o.data.materials.append(material('oak_light',True));be=o.modifiers.new('Highlighted rim','BEVEL');be.width=.022;be.segments=3;be.material=1
    for yy in [-dep-.005,dep+.005]:path('Purfling',[(x*.96,yy,z*.98+.012) for x,z in outline]+[(outline[0][0]*.96,yy,outline[0][1]*.98+.012)],.008,'oak_dark')
    cube('Neck',(0,0,(necktop+.90)/2),(.075,.10,necktop-.90),'oak_dark',.012)
    cube('Fingerboard',(0,-.075,(necktop+.68)/2),(.072,.035,necktop-.68),'black',.008)
    cube('Bridge',(0,-dep-.035,.39),(.19,.05,.065),'ivory',.008)
    cube('Tailpiece',(0,-dep-.028,.24),(.08,.025,.17),'black',.01)
    for i in range(4 if kind=='cello' else 6):
        x=(i-1.5)*.014 if kind=='cello' else (i-2.5)*.009
        rod('String',(x,-dep-.066,.28),(x,-.10,necktop),.0018,'ivory',6)
    for z in [necktop-.12,necktop-.035]:
        rod('Peg',( -.13,0,z),(.13,0,z),.018,'oak_dark')
        for x in [-.13,.13]:sphere('Peg grip',(x,0,z),(.025,.018,.035),'black')
    sphere('Scroll',(0,0,necktop+.07),(.065,.06,.085),'oak')
    if kind=='cello':
        for sign in [-1,1]:path('F hole',[(sign*.15,-dep-.029,.70),(sign*.12,-dep-.03,.65),(sign*.16,-dep-.03,.57),(sign*.13,-dep-.03,.49)],.012,'black')
        rod('Endpin',(0,0,.02),(0,0,.14),.013,'black')
    else:
        o=cyl('Sound hole',(0,-dep-.026,.59),.075,.008,'black',24);o.rotation_euler.x=math.pi/2
        torus('Rosette',(0,-dep-.034,.59),.084,.009,'gold',(math.pi/2,0,0))
instrument('cello');finish('16_Cello',(2.20,1.13,.16),-.16,2048)
# Proper instrument cradle.
for x in [-.19,.19]:
 rod('Cradle foot',(x,-.22,.03),(x,.20,.03),.025,'black')
 rod('Cradle arm',(x,.07,.03),(x,.07,.38),.024,'black')
 rod('Cradle fork',(x,.07,.31),(x,-.09,.34),.022,'black')
finish('17_Cello_Stand',(2.20,1.13,.08),-.16,512)
# Large fitted case simplified scalloped outline.
profile=[(-.14,0),(-.36,.16),(-.36,.60),(-.20,.90),(-.15,1.44),(-.12,1.65),(.12,1.65),(.15,1.44),(.20,.90),(.36,.60),(.36,.16),(.14,0)]
n=len(profile);v=[(x,y,z) for y in [-.10,.10] for x,z in profile]
o=mesh('Cello case',v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'blue');o.data.materials.append(material('blue',True));be=o.modifiers.new('Rounded case piping','BEVEL');be.width=.04;be.segments=3;be.material=1
for z in [.3,.75,1.15]:cube('Case latch',(.32 if z<.8 else .16,-.12,z),(.04,.026,.065),'gold',.005)
finish('18_Cello_Case',(2.57,1.93,.08),-.20,1024)
# Wall lute: local body faces -Y; hang on left wall facing +X.
instrument('lute');finish('19_Wall_Lute',(-2.75,.69,2.19),math.pi/2,1024)
# Bookshelf.
for x in [-.28,.28]:cube('Shelf side',(x,0,1.13),(.07,.28,2.10),'oak',.012)
for z in [.1,.62,1.15,1.70,2.18]:cube('Shelf plank',(0,0,z),(.63,.34,.065),'oak_light',.014)
cube('Shelf back',(0,.145,1.13),(.57,.04,2.10),'oak_dark',.01)
finish('20_Tall_Bookshelf',(2.64,2.23,.60),res=1024)
# Book groups independent from furniture.
for group,(loc,num) in enumerate([((-2.43,.10,1.96),3),((2.65,2.14,1.28),4),((2.65,2.14,1.82),4),((-.90,2.12,1.45),3)]):
    for i in range(num):book((i*.075,0,0),(.065,.19,.28+random.random()*.10),['plum','sage','blue','oak'][i%4])
    finish('21_Book_Group_'+str(group+1),loc,0,512)
# Brass reading lamp on piano.
cyl('Lamp foot',(0,0,.025),.13,.045,'gold',24)
path('Lamp stem',[(0,0,.05),(0,0,.37),(.04,0,.48),(.17,0,.51),(.24,0,.44)],.017,'gold')
# bell shade open bottom, shell mesh
vs=[]
for z,r in [(.31,.17),(.40,.14),(.48,.065),(.50,.045)]:
 for i in range(24):a=i*2*math.pi/24;vs.append((.24+r*math.cos(a),r*math.sin(a),z))
fs=[]
for j in range(3):
 for i in range(24):a=j*24+i;b=j*24+(i+1)%24;fs.append((a,b,b+24,a+24))
mesh('Brass shade',vs,fs,'gold');sphere('Lamp bulb',(.24,0,.37),(.07,.07,.065),'ivory')
finish('22_Piano_Lamp',(-2.39,1.39,1.95),math.pi/2,1024)
# Basket, open with spiraled weave rings and broad reeds.
for j in range(13):
 z=.06+j*.034;r=.24+j*.003;torus('Basket weave',(0,0,z),r,.015,'oak_light')
for i in range(24):
 a=i*2*math.pi/24;rod('Basket reed',(.24*math.cos(a),.24*math.sin(a),.045),(.28*math.cos(a),.28*math.sin(a),.49),.011,'oak')
cyl('Basket bottom',(0,0,.045),.24,.035,'oak',24)
torus('Basket lip',(0,0,.49),.28,.022,'oak_light')
for x in [-.28,.28]:path('Handle',[(x,0,.40),(x,0,.64),(x,.14,.64),(x,.14,.40)],.02,'oak_light')
finish('23_Woven_Basket',(2.30,.34,.08),res=1024)
cloth('Basket cloth',(2.30,.34,.57),.34,.55,'plum',.30);finish('24_Basket_Cloth',res=512)
# Drum on its edge, local cylinder rotate to front.
o=cyl('Drum shell',(0,0,0),.29,.13,'oak',32);o.rotation_euler.x=math.pi/2
for y in [-.071,.071]:
 o=cyl('Drum skin',(0,y,0),.277,.009,'ivory',32);o.rotation_euler.x=math.pi/2
 torus('Drum rim',(0,y,0),.286,.013,'gold',(math.pi/2,0,0))
for i in range(12):
 a=i*math.pi/6;rod('Drum tension',(.293*math.cos(a),-.066,.293*math.sin(a)),(.293*math.cos(a),.066,.293*math.sin(a)),.007,'ivory')
finish('25_Frame_Drum',(2.32,.65,.61),-.1,1024)
# Plant pots and leaves: solid curved leaf mesh, pale central vein, no alpha cards.
def plant(name,loc,size=1,trailing=False):
    # pot
    cyl('Clay pot',(0,0,.12),.14,.24,'terracotta',20,r2=.19);torus('Pot rim',(0,0,.25),.19,.02,'oak_light');cyl('Soil',(0,0,.24),.17,.018,'soil',20)
    for branch in range(7):
        a=branch*2.399;pts=[]
        for j in range(7):
            t=j/6;r=.07+t*.32
            z=.26+(.52*t-.22*t*t if not trailing else .22*math.sin(t*math.pi)-t*.72)
            pts.append((r*math.cos(a),r*math.sin(a),z))
        path('Vine',pts,.009,'leaf')
        for j in range(1,7):
            p=Vector(pts[j]);angle=a+(-.85 if j%2 else .85);direction=Vector((math.cos(angle),math.sin(angle),.28));side=Vector((-math.sin(angle),math.cos(angle),0));le=.15+random.random()*.06
            vs=[p,p+direction*le*.35+side*le*.32,p+direction*le+Vector((0,0,.014)),p+direction*le*.35-side*le*.32,p+direction*le*.45+Vector((0,0,.04))]
            mesh('Leaf',vs,[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'leaf_light' if j%3==0 else 'leaf')
            rod('Leaf vein',p,p+direction*le,.0025,'sage_light',6)
    for ob in parts:
        ob.location*=size;ob.scale*=size
    finish(name,loc,res=1024)
plant('26_Piano_Plant',(-2.40,-.10,1.96),.82,True)
plant('27_Window_Plant',(-1.09,2.18,1.48),1.0,False)
plant('28_Shelf_Trailing_Plant',(2.62,2.20,2.84),.90,True)
# Hanging vine along upper wall.
pts=[(-2.80,-.85+i*.13,3.55-.09*math.sin(i*.4)) for i in range(26)];path('Hanging vine',pts,.013,'leaf')
for i,p in enumerate(pts):
 if i%2:
    x,y,z=p
    for side in [-1,1]:mesh('Ivy leaf',[(x,y,z),(x+.10,y+side*.04,z-.07),(x+.08,y+side*.13,z-.21),(x+.02,y+side*.18,z-.08)],[(0,1,2,3)],'leaf_light' if i%3==0 else 'leaf')
finish('29_Wall_Ivy',res=1024)
# Small framed manuscript above piano.
cube('Frame',(-2.815,-.56,2.66),(.065,.53,.68),'oak_light',.016)
cube('Parchment',(-2.773,-.56,2.66),(.012,.44,.59),'paper',.002)
for i in range(7):rod('Manuscript line',(-2.763,-.72,2.42+i*.065),(-2.763,-.43+(i%2)*.04,2.42+i*.065),.002,'ink',6)
finish('30_Framed_Music',res=512)
# Save the procedural editable source prior to UV and bake.
scene.cursor.location=(0,0,0)
# Lighting, camera and staging excluded from exports.
def area(name,loc,energy,color,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Key_Warm_Window',(1,-1,7),950,(1,.79,.55),5,(0,1,0))
area('Fill_Cool_Sky',(5,-4,4),500,(.67,.80,1),5,(0,0,1))
area('Rim_Soft',(-1,4,6),1300,(1,.87,.68),3,(0,0,1))
ld=bpy.data.lights.new('Piano_Lamp_Glow','POINT');ld.energy=14;ld.color=(1,.59,.26);ld.shadow_soft_size=.14;lo=bpy.data.objects.new('Piano_Lamp_Glow',ld);scene.collection.objects.link(lo);lo.location=(-2.15,1.39,2.31)
camd=bpy.data.cameras.new('Presentation_Camera');cam=bpy.data.objects.new('Presentation_Camera',camd);scene.collection.objects.link(cam);cam.location=(9,-12,9);target=Vector((0,.2,1.55));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=9.6;scene.camera=cam
# White studio ground is a render helper only.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.255));stage=bpy.context.object;stage.name='STUDIO_GROUND_do_not_export';stage.data.materials.append(material('ivory'))
scene.render.resolution_x=1400;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/Rehearsal_Nook_Procedural.blend'))
# UV unwrap each semantic object, independent non-overlapping atlas.
for idx,o in enumerate(assets):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.025,area_weight=.2,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
    o.data.uv_layers.active.name='UV0'
    print('UV',idx+1,len(assets),o.name,flush=True)
scene.render.filepath=str(R/'previews/01_procedural_preview.png');scene.cycles.samples=24
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/Rehearsal_Nook_UV_Source.blend'))
bpy.ops.render.render(write_still=True)
print('MODEL_COMPLETE',flush=True)
