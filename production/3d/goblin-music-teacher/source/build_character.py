import bpy, math, json, os, sys, random
from mathutils import Vector
from math import sin,cos,pi
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
random.seed(9)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection': bpy.data.collections.remove(c)
base=bpy.data.collections.get('Collection'); base.name='CHARACTER | separate editable meshes'
COL={}
for n in ['01 Head','02 Upper body','03 Lower body','04 Shoes','05 Hands','06 Eyes','07 Teeth','08 Hair','09 Eyebrows','10 Accessories','STUDIO']:
    c=bpy.data.collections.new(n); bpy.context.scene.collection.children.link(c); COL[n]=c
M={}
def mat(n,col,group,rough=.75):
    m=bpy.data.materials.new(n); m.diffuse_color=(*col,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*col,1); p.inputs['Roughness'].default_value=rough
    m['atlas']=group; m['paint_rgb']=list(col); M[n]=m; return m
mat('Moss gold skin',(.48,.52,.23),'01_Face',.78)
mat('Ear warm interior',(.55,.31,.20),'01_Face')
mat('Skin warm nose',(.53,.40,.22),'01_Face')
mat('Crease plum',(.12,.09,.065),'01_Face')
mat('Hand skin',(.48,.52,.23),'02_Hands')
mat('Nails',(.68,.64,.39),'02_Hands')
mat('Coat olive wool',(.24,.28,.135),'03_Upper')
mat('Coat lapel light',(.35,.39,.20),'03_Upper')
mat('Coat dark piping',(.14,.18,.08),'03_Upper')
mat('Cream waistcoat',(.76,.66,.46),'03_Upper')
mat('Cream cuff highlight',(.86,.77,.58),'03_Upper')
mat('Scarf terracotta',(.52,.20,.12),'04_Scarf')
mat('Scarf edge',(.70,.34,.19),'04_Scarf')
mat('Breeches umber',(.32,.29,.18),'05_Lower')
mat('Breeches seam',(.22,.20,.12),'05_Lower')
mat('Socks charcoal',(.115,.12,.10),'05_Lower')
mat('Leather cognac',(.29,.16,.075),'06_Shoes')
mat('Leather edge',(.46,.28,.13),'06_Shoes')
mat('Soles',(.075,.055,.04),'06_Shoes')
mat('Hair chestnut',(.125,.06,.025),'07_Hair')
mat('Hair swept highlights',(.27,.13,.052),'07_Hair')
mat('Brows espresso',(.05,.031,.019),'07_Hair')
mat('Ivory eyes',(.90,.85,.65),'08_EyesTeeth',.45)
mat('Iris amber',(.38,.21,.06),'08_EyesTeeth',.5)
mat('Pupil',(.025,.019,.012),'08_EyesTeeth',.45)
mat('Eye glint',(.98,.97,.87),'08_EyesTeeth',.3)
mat('Tooth ivory',(.92,.83,.60),'08_EyesTeeth')
mat('Brass',(.65,.42,.13),'09_Accessories',.48)
mat('Dark leather strap',(.18,.095,.045),'09_Accessories')
mat('Lute golden soundboard',(.67,.37,.12),'10_Lute')
mat('Lute ribs',(.30,.125,.045),'10_Lute')
mat('Lute binding',(.84,.59,.27),'10_Lute')
mat('Lute fretboard',(.09,.045,.023),'10_Lute')
mat('Lute strings',(.65,.57,.39),'10_Lute',.5)
def put(o,n,ma,collection):
    o.name=n
    for c in list(o.users_collection): c.objects.unlink(o)
    COL[collection].objects.link(o)
    if ma: o.data.materials.append(M[ma])
    for f in o.data.polygons: f.use_smooth=True
    return o
def mesh(n,v,f,ma,c):
    d=bpy.data.meshes.new(n); d.from_pydata(v,[],f); d.update(); o=bpy.data.objects.new(n,d); COL[c].objects.link(o)
    if ma:d.materials.append(M[ma])
    for p in d.polygons:p.use_smooth=True
    return o
def apply(o,mod):
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
def smooth(o,lev=1):
    m=o.modifiers.new('Shape smoothing','SUBSURF'); m.levels=lev; apply(o,m); return o
def uvball(n,p,s,ma,c,seg=24,rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=p);o=bpy.context.object;o.scale=s
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return put(o,n,ma,c)
def join(objs,n):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join();o=objs[0];o.name=n;return o
def tube(n,pts,rr,ma,c,sides=10,flatten=1):
    pts=[Vector(p) for p in pts];v=[];f=[]
    for i,p in enumerate(pts):
        t=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        a=t.cross(Vector((0,1,0)))
        if a.length<.05:a=t.cross(Vector((1,0,0)))
        a.normalize();b=t.cross(a).normalized()
        r=rr[i] if isinstance(rr,list) else rr
        for j in range(sides): v.append(tuple(p+r*(a*cos(2*pi*j/sides)+b*sin(2*pi*j/sides)*flatten)))
    for i in range(len(pts)-1):
        for j in range(sides):a=i*sides+j;b=i*sides+(j+1)%sides;f.append((a,b,b+sides,a+sides))
    f.extend([tuple(range(sides-1,-1,-1)),tuple((len(pts)-1)*sides+j for j in range(sides))])
    return mesh(n,v,f,ma,c)
def curve(n,pts,r,ma,c):
    d=bpy.data.curves.new(n,'CURVE');d.dimensions='3D';d.resolution_u=8;d.bevel_depth=r;d.bevel_resolution=2
    s=d.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(n,d);COL[c].objects.link(o);d.materials.append(M[ma]);bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.convert(target='MESH');o.select_set(False);return o
def panel(n,outline,thick,ma,c,bevel=.008):
    v=outline+[(x,y+thick,z) for x,y,z in outline];l=len(outline)
    f=[tuple(range(l-1,-1,-1)),tuple(range(l,l*2))]+[(i,(i+1)%l,(i+1)%l+l,i+l) for i in range(l)]
    o=mesh(n,v,f,ma,c)
    if bevel:
        m=o.modifiers.new('Soft tailored edges','BEVEL');m.width=bevel;m.segments=2;apply(o,m)
        m=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');apply(o,m)
    return o
def loft(n,rings,ma,c,seg=24,fold=0):
    v=[];f=[]
    for i,(x,y,z,rx,ry) in enumerate(rings):
        for j in range(seg):
            a=2*pi*j/seg; q=1+fold*sin(a*7+i*.65);v.append((x+rx*cos(a)*q,y+ry*sin(a)*q,z))
    for i in range(len(rings)-1):
        for j in range(seg): a=i*seg+j;b=i*seg+(j+1)%seg;f.append((a,b,b+seg,a+seg))
    f+=[tuple(range(seg-1,-1,-1)),tuple((len(rings)-1)*seg+j for j in range(seg))]
    return mesh(n,v,f,ma,c)
def ring(n,p,major,minor,ma,c,rot=(pi/2,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=p,major_radius=major,minor_radius=minor,rotation=rot)
    return put(bpy.context.object,n,ma,c)
def button(n,p,r=.012):return uvball(n,p,(r,.006,r),'Brass','10 Accessories',16,8)

# Contiguous sculpted head. Nose, cheeks and chin are fused into one closed volume.
headparts=[uvball('Head base',(0,.02,1.455),(.211,.161,.221),'Moss gold skin','01 Head',40,28),
uvball('Jaw',(0,-.025,1.345),(.165,.125,.09),'Moss gold skin','01 Head'),
uvball('Muzzle',(0,-.115,1.385),(.136,.065,.065),'Moss gold skin','01 Head'),
uvball('Nose bridge',(0,-.138,1.472),(.043,.058,.09),'Moss gold skin','01 Head'),
uvball('Nose bulb',(0,-.197,1.432),(.065,.061,.041),'Moss gold skin','01 Head')]
for s in [-1,1]:headparts.append(uvball('Cheek',(s*.139,-.075,1.415),(.064,.078,.063),'Moss gold skin','01 Head'))
head=join(headparts,'Head | sculpted face')
m=head.modifiers.new('Unified sculpt','REMESH');m.mode='VOXEL';m.voxel_size=.007;apply(head,m)
m=head.modifiers.new('Polish','SMOOTH');m.factor=1.1;m.iterations=4;apply(head,m)
m=head.modifiers.new('Sculpt density','DECIMATE');m.ratio=.48;apply(head,m)
for p in head.data.polygons:p.use_smooth=True
uvball('Neck',(0,.025,1.235),(.095,.085,.15),'Moss gold skin','01 Head')
# Long concave leaf ears, each with a warm inset and a rounded rim.
for s,side in [(-1,'R'),(1,'L')]:
    outline=[(.165,-.005,1.51),(.255,.006,1.57),(.49,.04,1.755),(.435,.018,1.545),(.335,-.018,1.425),(.23,-.036,1.408),(.176,-.043,1.445)]
    outline=[(s*x,y,z) for x,y,z in outline]
    center=(s*.29,.015,1.511);v=[center]+outline+[(x,y+.035,z) for x,y,z in outline]+[(s*.29,.065,1.511)]
    f=[];l=len(outline)
    for j in range(l):f.extend([(0,1+j,1+(j+1)%l),(1+j,1+l+j,1+l+(j+1)%l,1+(j+1)%l),(1+l+j,len(v)-1,1+l+(j+1)%l)])
    o=smooth(mesh('Ear.'+side,v,f,'Moss gold skin','01 Head'),2)
    inner=[(s*.228,-.014,1.485),(s*.278,-.004,1.537),(s*.449,.025,1.70),(s*.387,-.001,1.529),(s*.30,-.018,1.455)]
    panel('Ear inset.'+side,inner,.006,'Ear warm interior','01 Head',.009)
    curve('Ear helix.'+side,[(s*.207,-.04,1.446),(s*.273,-.026,1.47),(s*.33,-.015,1.525),(s*.442,.02,1.69)],.008,'Moss gold skin','01 Head')
    # Alert half-lidded amber eyes.
    parts=[uvball('Sclera',(s*.092,-.141,1.49),(.055,.029,.024),'Ivory eyes','06 Eyes',32,16),
           uvball('Iris',(s*.086,-.169,1.487),(.016,.004,.017),'Iris amber','06 Eyes',24,16),
           uvball('Pupil',(s*.086,-.173,1.487),(.007,.002,.012),'Pupil','06 Eyes',20,12),
           uvball('Catchlight',(s*.086-.004,-.175,1.493),(.003,.0015,.003),'Eye glint','06 Eyes',12,8)]
    join(parts,'Eye.'+side+' | globe iris pupil')
    curve('Upper eyelid.'+side,[(s*.039,-.149,1.494),(s*.074,-.168,1.507),(s*.12,-.151,1.505),(s*.145,-.122,1.491)],.010,'Moss gold skin','01 Head')
    curve('Lower eyelid.'+side,[(s*.039,-.146,1.489),(s*.088,-.165,1.472),(s*.131,-.137,1.479),(s*.145,-.122,1.491)],.006,'Moss gold skin','01 Head')
    curve('Under eye crease.'+side,[(s*.048,-.15,1.455),(s*.104,-.143,1.448),(s*.14,-.117,1.46)],.0023,'Crease plum','01 Head')
    curve('Nostril.'+side,[(s*.02,-.248,1.417),(s*.039,-.243,1.412),(s*.051,-.225,1.422)],.0038,'Crease plum','01 Head')
    brow=tube('Eyebrow.'+side,[(s*.024,-.148,1.55),(s*.04,-.166,1.562),(s*.08,-.165,1.555),(s*.125,-.144,1.548),(s*.163,-.111,1.536)],[.009,.021,.021,.017,.002],'Brows espresso','09 Eyebrows',8,.48)
    smooth(brow,1)
    for k in range(2):
        tube('Fang.'+side+str(k+1),[(s*(.092+k*.035),-.174+k*.012,1.366),(s*(.096+k*.035),-.188+k*.013,1.383),(s*(.099+k*.035),-.18+k*.015,1.402-k*.012)],[.014-k*.003,.011-k*.003,.0008],'Tooth ivory','07 Teeth',10)
curve('Smile crease',[(-.146,-.119,1.398),(-.119,-.158,1.371),(0,-.182,1.357),(.119,-.158,1.371),(.146,-.119,1.398)],.0037,'Crease plum','01 Head')
curve('Lower lip', [(-.08,-.174,1.345),(0,-.181,1.34),(.08,-.174,1.345)],.005,'Moss gold skin','01 Head')

# Waistcoat and coat: front opening, pointed lapels, side panels and tails.
smooth(loft('Waistcoat torso',[(0,.035,.755,.16,.112),(0,.02,.79,.205,.14),(0,.015,.93,.217,.15),(0,.025,1.08,.20,.139),(0,.03,1.18,.13,.09)],'Cream waistcoat','02 Upper body'),1)
panel('Waistcoat pointed hem',[(-.18,-.112,.82),(0,-.153,.73),(.18,-.112,.82),(0,-.16,.90)],.024,'Cream waistcoat','02 Upper body')
for z in [.84,.90,.96,1.02]:button('Waistcoat button',(.0,-.146,z),.010)
for s,side in [(-1,'R'),(1,'L')]:
    panel('Coat front.'+side,[(s*.145,-.075,1.19),(s*.26,-.013,1.13),(s*.255,-.057,.98),(s*.315,-.035,.755),(s*.195,-.13,.79),(s*.115,-.15,.86),(s*.148,-.125,1.055)],.06,'Coat olive wool','02 Upper body',.012)
    panel('Lapel.'+side,[(s*.105,-.11,1.205),(s*.30,-.068,1.185),(s*.217,-.136,1.107),(s*.27,-.118,1.082),(s*.125,-.177,.886),(s*.149,-.155,1.05)],.02,'Coat lapel light','02 Upper body',.005)
    curve('Lapel piping.'+side,[(s*.105,-.12,1.205),(s*.30,-.08,1.185),(s*.217,-.148,1.107),(s*.27,-.13,1.082),(s*.125,-.189,.886)],.003,'Coat dark piping','02 Upper body')
    panel('Coat tail.'+side,[(s*.12,.11,1.09),(s*.23,.085,.93),(s*.32,.10,.64),(s*.16,.153,.59),(s*.035,.16,.76),(s*.025,.15,1.07)],.028,'Coat olive wool','02 Upper body',.01)
    button('Coat front button.'+side,(s*.195,-.13,.842),.012)
    # Arms are lowered ~40 degrees from horizontal, fingers accessible for edits.
    upper=[(s*.21,.025,1.12),(s*.27,.02,1.105),(s*.34,.005,1.035),(s*.40,-.01,.975),(s*.442,-.026,.921),(s*.491,-.04,.85),(s*.52,-.045,.81)]
    smooth(tube('Coat sleeve.'+side,upper,[.094,.096,.089,.078,.087,.083,.075],'Coat olive wool','02 Upper body',20),2)
    smooth(tube('Turned cuff.'+side,[(s*.468,-.035,.889),(s*.48,-.04,.873),(s*.519,-.047,.815),(s*.525,-.05,.805)],[.091,.092,.084,.083],'Cream cuff highlight','02 Upper body',16),1)
    curve('Sleeve seam.'+side,[(s*.25,-.061,1.12),(s*.33,-.074,1.038),(s*.406,-.081,.969),(s*.469,-.113,.89)],.0028,'Coat dark piping','02 Upper body')
    for k in range(2):button('Cuff button.'+side+str(k),(s*(.486+k*.02),-.115,.862-k*.029),.009)
    # Joined palm and five tapered articulated digits; independent left/right hands.
    hp=[uvball('Palm',(s*.548,-.051,.772),(.048,.033,.065),'Hand skin','05 Hands')]
    for k in range(4):
        x=s*(.518+k*.021);z=.741+abs(k-1.5)*.006;y=-.057
        pts=[(x,y,z),(x+s*.011,y-.006,z-.032),(x+s*.012,y-.018,z-.058),(x+s*.007,y-.027,z-.066)]
        hp.append(smooth(tube('Finger',pts,[.013,.013,.011,.006],'Hand skin','05 Hands',8),1))
        hp.append(uvball('Nail',(x+s*.009,y-.035,z-.056),(.007,.002,.01),'Nails','05 Hands',12,8))
    hp.append(smooth(tube('Thumb',[(s*.522,-.05,.795),(s*.491,-.067,.77),(s*.488,-.085,.749),(s*.5,-.091,.739)],[.019,.018,.014,.008],'Hand skin','05 Hands'),1))
    join(hp,'Hand.'+side+' | five fingers and nails')
    # Full breeches with pinched knees and clear central crotch separation.
    smooth(loft('Breeches.'+side,[(s*.105,.025,.79,.119,.13),(s*.13,.025,.748,.147,.153),(s*.151,.018,.63,.16,.157),(s*.17,.0,.51,.126,.134),(s*.172,-.006,.46,.081,.09)],'Breeches umber','03 Lower body',32,.035),1)
    smooth(loft('Breeches knee band.'+side,[(s*.172,-.006,.46,.084,.094),(s*.171,-.007,.438,.082,.09),(s*.17,-.007,.423,.075,.085)],'Cream waistcoat','03 Lower body',24),1)
    # Reassign knee bands to lower atlas through their own material.
    o=bpy.context.object
    smooth(loft('Stocking.'+side,[(s*.17,.0,.44,.062,.067),(s*.175,.009,.35,.058,.061),(s*.178,.004,.237,.044,.047)],'Socks charcoal','03 Lower body',20),1)
    for j in range(4):
        z=.27+j*.035
        curve('Stocking knit.'+side+str(j),[(s*.22,-.013,z),(s*.18,-.047,z-.006),(s*.135,-.013,z)],.0015,'Breeches seam','03 Lower body')
    curve('Trouser seam.'+side,[(s*.263,-.045,.735),(s*.303,-.065,.62),(s*.27,-.06,.51),(s*.225,-.057,.465)],.0025,'Breeches seam','03 Lower body')
    # Curved pointed shoes extend forward and outward, with distinct sole and cuff.
    x=s*.18
    path=[(x,.045,.16),(x,.0,.128),(x+s*.015,-.09,.105),(x+s*.045,-.175,.092),(x+s*.08,-.235,.095),(x+s*.12,-.29,.13)]
    shoe=smooth(tube('Shoe upper.'+side,path,[.052,.074,.079,.064,.037,.0015],'Leather cognac','04 Shoes',16,.64),2)
    solepath=[(x,.049,.102),(x,-.01,.071),(x+s*.018,-.1,.054),(x+s*.05,-.19,.049),(x+s*.085,-.245,.064),(x+s*.121,-.291,.126)]
    smooth(tube('Shoe sole.'+side,solepath,[.055,.076,.079,.059,.032,.001],'Soles','04 Shoes',12,.18),1)
    smooth(loft('Boot ankle.'+side,[(x,.006,.12,.065,.06),(x,.006,.21,.052,.05),(x,.006,.258,.054,.052)],'Leather cognac','04 Shoes',20),1)
    panel('Boot turned cuff.'+side,[(x-s*.06,-.046,.285),(x,-.067,.257),(x+s*.065,-.038,.28),(x+s*.041,-.06,.207),(x-s*.035,-.063,.211)],.012,'Leather edge','04 Shoes')
    for j in range(3):
        y=-.055-j*.037;z=.182-j*.022
        curve('Boot lace.'+side+str(j),[(x-s*.035,y,z-.004),(x+s*.015,y-.013,z+.004),(x+s*.037,y-.007,z-.005)],.003,'Leather edge','04 Shoes')
    button('Boot buckle.'+side,(x+s*.047,-.048,.211),.011)

# Wrapped scarf with asymmetric fabric ridges, knot and dangling end.
backrings=[(.79,.207,.172),(.88,.228,.18),(1.02,.225,.174),(1.12,.209,.158),(1.19,.118,.106)]
vv=[];ff=[];bn=24
for z,rx,ry in backrings:
    for j in range(bn+1):
        a=pi*j/bn;vv.append((rx*cos(a),.03+ry*sin(a),z))
for i in range(len(backrings)-1):
    for j in range(bn):
        a=i*(bn+1)+j;ff.append((a,a+1,a+bn+2,a+bn+1))
back=mesh('Coat back',vv,ff,'Coat olive wool','02 Upper body');smooth(back,2)
mod=back.modifiers.new('Tailored thickness','SOLIDIFY');mod.thickness=.018;apply(back,mod)
for o in COL['02 Upper body'].objects:
    if o.name.startswith('Coat tail.'):o.location.y+=.10
sc=loft('Scarf wrap',[(0,.012,1.17,.09,.085),(0,.006,1.19,.138,.121),(0,-.006,1.24,.159,.143),(0,-.006,1.31,.155,.137),(0,.0,1.328,.145,.129)],'Scarf terracotta','02 Upper body',40,.018);smooth(sc,1)
for k in range(3):
    z=1.207+k*.034
    curve('Scarf fold '+str(k),[(-.135,-.078,z+.035),(-.09,-.139,z+.012),(0,-.151,z),(.095,-.123,z-.005),(.143,-.057,z+.018)],.0045,'Scarf edge','02 Upper body')
panel('Scarf hanging end',[(.055,-.11,1.20),(.102,-.087,1.18),(.10,-.155,1.052),(.035,-.162,1.09)],.014,'Scarf terracotta','02 Upper body',.006)
for s in [-1,1]:panel('Shirt collar',[(s*.06,-.09,1.18),(s*.10,-.105,1.15),(s*.04,-.145,1.10),(0,-.123,1.18)],.01,'Cream cuff highlight','02 Upper body',.004)

# Sculpted swept hair cap and broad directional locks; no alpha cards.
v=[];f=[];rows=9;segs=40
for i in range(rows):
    for j in range(segs):
        a=2*pi*j/segs
        end=1.68 + .75*sin(a) # open forehead and longer nape
        t=.03+(end-.03)*i/(rows-1)
        v.append((.216*sin(t)*cos(a),.025+.169*sin(t)*sin(a),1.47+.221*cos(t)))
for i in range(rows-1):
    for j in range(segs):a=i*segs+j;b=i*segs+(j+1)%segs;f.append((a,b,b+segs,a+segs))
cap=mesh('Hair cap',v,f,'Hair chestnut','08 Hair');m=cap.modifiers.new('Hair thickness','SOLIDIFY');m.thickness=.012;apply(cap,m);smooth(cap,1)
for j in range(5):
    x=-.15+j*.052;lift=.017*sin(j*.8)
    pts=[(x,-.117+j*.005,1.607+lift),(x-.023,-.112,1.674+lift),(x+.025,-.052,1.745+lift),(x+.092,.025,1.739+lift),(x+.135,.099,1.675+lift)]
    o=tube('Swept forelock %02d'%j,pts,[.018,.045,.05,.032,.0015],'Hair chestnut','08 Hair',10,.38);smooth(o,2)
    curve('Hair brush ridge %02d'%j,[(p[0]-.004,p[1]-.009,p[2]+.01) for p in pts[1:-1]],.0017,'Hair swept highlights','08 Hair')
for s,side in [(-1,'R'),(1,'L')]:
    for k in range(3):
        pts=[(s*.168,.0+k*.055,1.613),(s*.21,-.012+k*.048,1.567),(s*.209,-.026+k*.04,1.49),(s*.181,-.055+k*.04,1.415-k*.013)]
        smooth(tube('Temple lock.'+side+str(k),pts,[.027,.028,.021,.0015],'Hair chestnut','08 Hair',10,.6),1)
    # Gold rings through the outer ears.
    for k in range(2):ring('Ear hoop.'+side+str(k),(s*(.365+k*.052),.001,1.491+k*.092),.023-k*.003,.004,'Brass','10 Accessories')
    uvball('Ear stud.'+side,(s*.229,-.039,1.427),(.009,.006,.009),'Brass','10 Accessories',12,8)
    ring('Ear pendant.'+side,(s*.299,-.016,1.421),.016,.0035,'Brass','10 Accessories')

# Leather music satchel/strap and small brass fastenings.
curve('Lute shoulder strap', [(-.18,-.088,1.177),(-.10,-.185,1.066),(.02,-.186,.96),(.16,-.181,.845),(.25,-.12,.765),(.25,.12,.79),(.05,.19,1.02),(-.18,.09,1.175)],.019,'Dark leather strap','10 Accessories')
panel('Belt tab',[(-.16,-.145,.81),(-.13,-.145,.812),(-.16,-.164,.725),(-.193,-.153,.74)],.015,'Dark leather strap','10 Accessories',.004)
ring('Belt ring',(-.172,-.162,.728),.014,.003,'Brass','10 Accessories')

# Separate lute: pear-shaped bowl, golden soundboard, rosette, frets and strings.
# Model in local XZ plane, then rotate the entire instrument together.
L=[]
outline=[]
for j in range(48):
    a=2*pi*j/48
    z=.155*cos(a);w=.106*(1-.38*cos(a));outline.append((w*sin(a),-.04,z))
v=[(0,.047,-.025)]+[(x,y+.07,z) for x,y,z in outline]+outline
f=[]
for j in range(48):f.extend([(0,1+(j+1)%48,1+j),(1+j,1+(j+1)%48,49+(j+1)%48,49+j)])
L.append(smooth(mesh('Lute bowl',v,f,'Lute ribs','10 Accessories'),2))
L.append(panel('Lute soundboard',outline,.012,'Lute golden soundboard','10 Accessories',.002))
L.append(curve('Lute binding',outline+[outline[0]],.0035,'Lute binding','10 Accessories'))
L.append(uvball('Lute soundhole',(0,-.044,.028),(.033,.002,.033),'Lute fretboard','10 Accessories',32,12))
L.append(ring('Lute rosette',(0,-.048,.028),.036,.003,'Lute binding','10 Accessories'))
for j in range(8):
    a=j*pi/4
    L.append(curve('Rosette carved spoke',[(.03*cos(a),-.051,.028+.03*sin(a)),(.011*cos(a+.5),-.052,.028+.011*sin(a+.5)),(.028*cos(a+1),-.051,.028+.028*sin(a+1))],.0015,'Lute binding','10 Accessories'))
L.append(panel('Lute neck',[(-.019,-.035,.12),(.019,-.035,.12),(.017,-.035,.365),(-.017,-.035,.365)],.035,'Lute ribs','10 Accessories',.003))
L.append(panel('Lute fingerboard',[(-.021,-.043,.12),(.021,-.043,.12),(.018,-.043,.37),(-.018,-.043,.37)],.008,'Lute fretboard','10 Accessories',.001))
L.append(panel('Lute peghead',[(-.024,-.04,.354),(.024,-.04,.354),(.03,-.035,.437),(-.03,-.035,.437)],.025,'Lute ribs','10 Accessories',.004))
L.append(panel('Lute bridge',[(-.045,-.052,-.079),(.045,-.052,-.079),(.045,-.052,-.066),(-.045,-.052,-.066)],.008,'Lute fretboard','10 Accessories',.001))
for j in range(9):
    z=.14+j*.023
    L.append(curve('Lute fret', [(-.02,-.052,z),(.02,-.052,z)],.001,'Lute strings','10 Accessories'))
for j in range(4):
    x=-.012+j*.008
    L.append(curve('Lute string',[(x,-.059,-.075),(x,-.055,.37),(x,-.045,.413)],.00065,'Lute strings','10 Accessories'))
    s= -1 if j%2==0 else 1;z=.377+(j//2)*.034
    L.append(tube('Lute peg stem',[(s*.022,-.023,z),(s*.042,-.023,z)],.004,'Lute binding','10 Accessories',8))
    L.append(uvball('Lute tuning peg',(s*.045,-.023,z),(.008,.008,.012),'Lute ribs','10 Accessories',12,8))
from mathutils import Matrix
T=Matrix.Translation((.26,-.255,.76))@Matrix.Rotation(.46,4,'Y')
for o in L:o.matrix_world=T@o.matrix_world

# Assign knee cuff material to its own atlas, preventing separate objects from sharing islands.
m=M['Cream waistcoat'].copy();m.name='Knee cuff cream';m['atlas']='05_Lower'
for o in COL['03 Lower body'].objects:
    if 'knee band' in o.name:o.data.materials.clear();o.data.materials.append(m)
# Consolidate tiny musical components into useful editable assemblies.
for starts,name in [('Lute string','Lute strings'),('Lute fret','Lute frets'),('Lute tuning peg','Lute tuning pegs'),('Lute peg stem','Lute peg stems'),('Rosette carved','Lute rosette carving')]:
    objs=[o for o in list(COL['10 Accessories'].objects) if o.name.startswith(starts)]
    if len(objs)>1:join(objs,name)

# Apply transforms and mark semantic role. Scale to a 1.45 m goblin including hair/ears.
for o in list(bpy.data.objects):
    if o.name.startswith(('Lapel piping.','Sleeve seam.','Trouser seam.')):bpy.data.objects.remove(o,do_unlink=True)
S=.82
for o in list(bpy.data.objects):
    if o.type!='MESH':continue
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    if o.name=='Lute shoulder strap':
        for v in o.data.vertices:
            if v.co.y>0:v.co.y+=.075*min(1,v.co.y/.05)
    for v in o.data.vertices:v.co*=S
    o['part_category']=o.users_collection[0].name
    o['texture_style']='Authored painterly color, broad form shading, selective directional strokes'

scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
scene.world.color=(.18,.18,.18)
scene.view_settings.view_transform='AgX'
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(n,p,power,size,color):
    d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(n,d);COL['STUDIO'].objects.link(o);o.location=p;aim(o,(0,0,.8))
area('Warm key',(-2,-3,4),420,3,(1,.84,.65));area('Cool fill',(2,-1,2),210,2,(.65,.79,1));area('Hair rim',(0,2,3),500,2,(1,.77,.48))
d=bpy.data.cameras.new('Character portrait');cam=bpy.data.objects.new('Character portrait',d);COL['STUDIO'].objects.link(cam);cam.location=(2.0,-5,2.1);aim(cam,(0,0,.76));d.type='ORTHO';d.ortho_scale=1.82;scene.camera=cam
groundmat=bpy.data.materials.new('Studio warm paper');groundmat.diffuse_color=(.25,.28,.25,1)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,.01));o=bpy.context.object;put(o,'Studio floor',None,'STUDIO');o.data.materials.append(groundmat)
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_distance=2.3;a.spaces.active.region_3d.view_location=(0,0,.78)
        a.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');head.select_set(True);bpy.context.view_layer.objects.active=head
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/Goblin_Model_Source.blend'))
scene.render.filepath=str(ROOT/'previews/01_shape_review.png');bpy.ops.render.render(write_still=True)
print('BUILD_COMPLETE',flush=True)
