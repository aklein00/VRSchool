"""Author layered, seam-consistent painterly textures from the actual UV surfaces.
No concept image is projected: all color and brush layers are authored here.
"""
from pathlib import Path
import numpy as np, json, io, zipfile, xml.etree.ElementTree as ET,os
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[1]
report={}
ONLY=os.environ.get('VRHS_ATLAS')
if ONLY:report=json.loads((ROOT/'source/texture-validation.json').read_text())
def pngbytes(im):
    f=io.BytesIO();im.save(f,format='PNG');return f.getvalue()
def ora(path,layers,flat):
    root=ET.Element('image',w=str(flat.width),h=str(flat.height),name=path.stem,version='0.0.3');stack=ET.SubElement(root,'stack')
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
        for i,(name,im,visible) in enumerate(layers):
            src=f'data/layer{i:02d}.png';z.writestr(src,pngbytes(im));ET.SubElement(stack,'layer',{'name':name,'src':src,'opacity':'1.0','visibility':'visible' if visible else 'hidden','composite-op':'svg:src-over','x':'0','y':'0'})
        z.writestr('stack.xml',ET.tostring(root));z.writestr('mergedimage.png',pngbytes(flat));thumb=flat.copy();thumb.thumbnail((256,256));z.writestr('Thumbnails/thumbnail.png',pngbytes(thumb))
for path in sorted((ROOT/'source').glob('*_surface.npz')):
    g=path.stem.replace('_surface','');d=np.load(path);tri=d['triangles'];n=int(d['resolution'])
    if ONLY and g not in ONLY.split(','):continue
    print('PAINT',g,n,len(tri),flush=True)
    fields=np.zeros((n,n,11),np.float32);cover=np.zeros((n,n),np.uint16)
    for t in tri:
        uv=t[:,:2].copy();uv[:,0]*=n;uv[:,1]=(1-uv[:,1])*n
        xmin=max(0,int(np.floor(uv[:,0].min())));xmax=min(n-1,int(np.ceil(uv[:,0].max())))
        ymin=max(0,int(np.floor(uv[:,1].min())));ymax=min(n-1,int(np.ceil(uv[:,1].max())))
        if xmax<xmin or ymax<ymin:continue
        a,b,c=uv;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-8:continue
        yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];xx=xx+.5;yy=yy+.5
        w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w2=1-w0-w1
        inside=(w0>=0)&(w1>=0)&(w2>=0)
        if not inside.any():continue
        fields[ymin:ymax+1,xmin:xmax+1][inside]=(w0[...,None]*t[0,2:]+w1[...,None]*t[1,2:]+w2[...,None]*t[2,2:])[inside]
        strict=(w0>1e-4)&(w1>1e-4)&(w2>1e-4);cover[ymin:ymax+1,xmin:xmax+1]+=strict
    valid=np.linalg.norm(fields[:,:,3:6],axis=2)>.1
    # Extend paint beyond islands, with nearest-island ownership in shared gutters.
    dist,nearest=distance_transform_edt(~valid,return_indices=True);pad=(dist<=8)
    fields[~valid & pad]=fields[nearest[0][~valid & pad],nearest[1][~valid & pad]]
    pos=fields[:,:,:3];normal=fields[:,:,3:6];normal/=np.maximum(np.linalg.norm(normal,axis=2,keepdims=True),1e-7)
    base=fields[:,:,6:9].copy();rough=fields[:,:,9]
    x,y,z=pos[:,:,0],pos[:,:,1],pos[:,:,2]
    alpha=pad.astype(np.float32)
    # Palette entries are deliberate sRGB pigments; broad strokes stay in world space across seams.
    base[~pad]=(.13,.12,.10)
    flats=Image.fromarray(np.uint8(np.clip(base,0,1)*255),'RGB').convert('RGBA')
    def layer(rgb,a):
        out=np.empty((n,n,4),np.uint8)
        out[:,:,:3]=np.uint8(np.clip(rgb,0,1)*255)
        out[:,:,3]=np.uint8(np.clip(a*alpha,0,1)*255)
        return Image.fromarray(out,'RGBA')
    # Fixed painted shading is restrained; the material still responds to scene lights.
    light=np.array([-.38,-.42,.82]);nd=normal@light
    shade=np.clip(.10-.18*nd,0,.28)
    shade*=.65 if g=='08_EyesTeeth' else 1
    shadows=layer((.10,.075,.09),shade)
    highlight=np.clip((nd-.12)*.20,0,.17)
    highlights=layer((.95,.78,.46),highlight)
    wash=(np.sin(x*31+z*22+np.sin(y*19))*np.sin(z*37-y*16)+1)*.5
    wash*=np.clip(np.abs(normal[:,:,0])*.7+.15,0,1)
    wash*=.09
    pigment=layer((.69,.51,.27),wash)
    # Warm nose, cheeks and knuckles. Kept separate for easy palette changes.
    accents=np.zeros((n,n),np.float32)
    if g=='01_Face':
        nose=np.exp(-((x/.047)**2+((z-1.427*.82)/.035)**2+((y+.195*.82)/.035)**2)*1.3)
        cheeks=np.exp(-(((np.abs(x)-.12*.82)/.043)**2+((z-1.412*.82)/.03)**2+((y+.131*.82)/.035)**2)*1.5)
        accents=.32*nose+.16*cheeks
    elif g=='02_Hands':accents=.13*np.maximum(0,-normal[:,:,1])*(.5+.5*np.sin(z*89))
    warm=layer((.66,.30,.18),np.clip(accents,0,.4))
    # Selective thin hatching in shadow planes; no uniform mottling or distressed noise.
    freq=260 if g!='07_Hair' else 420
    stripe=np.maximum(0,np.sin((x*.55+z+y*.18)*freq+np.sin(z*31)*2))**16
    gate=np.maximum(0,np.sin(x*47-z*19+y*31)-.25)*np.clip(-nd+.12,0,.6)
    strokes=layer((.12,.075,.045),stripe*gate*.17)
    # Finer wood grain only on the lute; hair gets elongated chestnut brush marks.
    if g in ['10_Lute','07_Hair']:
        stripe=(np.sin(x*(500 if g=='10_Lute' else 230)+y*65+np.sin(z*27)*2)*.5+.5)**22
        strokes=layer((.12,.055,.02),stripe*.13*np.clip(1-abs(normal[:,:,2]),.15,1))
    uv=Image.new('RGBA',(n,n),(0,0,0,0));draw=ImageDraw.Draw(uv)
    for poly in json.loads((ROOT/'uv-layouts'/f'{g}_polygons.json').read_text()):
        xy=[(a*n,(1-b)*n) for a,b in poly];draw.line(xy+[xy[0]],fill=(64,210,235,115),width=1)
    uv.save(ROOT/'uv-layouts'/f'{g}_UV.png')
    edit=Image.new('RGBA',(n,n),(0,0,0,0))
    layers=[('UV guide - HIDDEN for export',uv,False),('Your paint edits',edit,True),('Selective brush strokes',strokes,True),('Warm facial accents',warm,True),('Warm edge highlights',highlights,True),('Broad pigment washes',pigment,True),('Cool form shadows',shadows,True),('Base color palette',flats,True)]
    flat=Image.new('RGBA',(n,n))
    for name,im,vis in reversed(layers):
        if vis:flat=Image.alpha_composite(flat,im)
    flat.convert('RGB').save(ROOT/'textures'/f'{g}_BaseColor.png')
    r=np.uint8(np.clip(np.where(pad,rough,.8),0,1)*255);Image.fromarray(r,'L').save(ROOT/'textures'/f'{g}_Roughness.png')
    ora(ROOT/'gimp'/f'{g}_Paint.ora',layers,flat)
    report[g]={'resolution':n,'layers':len(layers),'covered_pixels':int(valid.sum()),'overlap_pixels_interior':int((cover>1).sum()),'overlap_percent':float(100*(cover>1).sum()/max(1,valid.sum())),'maximum_dilation_pixels':8}
    print('PAINT_DONE',g,report[g],flush=True)
(ROOT/'source/texture-validation.json').write_text(json.dumps(report,indent=2))
