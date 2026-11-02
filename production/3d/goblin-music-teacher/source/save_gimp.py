from pathlib import Path
import json,os
from gi.repository import Gimp,Gio
ROOT=Path(__file__).resolve().parents[1]
report={}
ONLY=os.environ.get('VRHS_ATLAS')
if ONLY:report=json.loads((ROOT/'source/gimp-validation.json').read_text())
for p in sorted((ROOT/'gimp').glob('*.ora')):
    if ONLY and not any(p.name.startswith(g) for g in ONLY.split(',')):continue
    im=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(p)))
    assert im is not None,str(p)
    layers=im.get_layers();assert len(layers)==8,(p,len(layers))
    layers[0].set_visible(False)
    dest=p.with_suffix('.xcf')
    assert Gimp.file_save(Gimp.RunMode.NONINTERACTIVE,im,Gio.File.new_for_path(str(dest)),None)
    im.delete()
    check=Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,Gio.File.new_for_path(str(dest)))
    entries=[{'name':l.get_name(),'visible':l.get_visible(),'width':l.get_width(),'height':l.get_height()} for l in check.get_layers()]
    assert len(entries)==8 and not entries[0]['visible']
    g=p.stem.replace('_Paint','')
    # Export from the reopened XCF, so the Blender map matches GIMP's visible composition exactly.
    flat=check.duplicate();flat.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)
    assert Gimp.file_save(Gimp.RunMode.NONINTERACTIVE,flat,Gio.File.new_for_path(str(ROOT/'textures'/f'{g}_BaseColor.png')),None)
    report[g]={'xcf':dest.name,'width':check.get_width(),'height':check.get_height(),'reopened_in_gimp':True,'layers':entries}
    print('XCF_VERIFIED',dest.name,flush=True);flat.delete();check.delete()
(ROOT/'source/gimp-validation.json').write_text(json.dumps(report,indent=2))
