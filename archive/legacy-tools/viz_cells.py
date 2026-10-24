import sys, struct
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
import numpy as np
from PIL import Image
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc"); TEX=game+"textures.vpp_pc"
def hdr(path):
    with open(path,'rb') as f: d=f.read(5+0x14F+20)
    o=5+0x14F; num,cs,lo,lf,le=struct.unpack_from('<iiiii',d,o)
    names_at=((0x800+lo)&0xFFFFF800)+0x800; ext_at=((names_at+lf)&0xFFFFF800)+0x800
    data_start=((ext_at+le)&0xFFFFF800)+0x800
    return num,data_start,names_at,ext_at,lo,lf,le
def read_atlas(vp,name,ext=None):
    e=vp.find(name,ext) if ext else None
    if e is None:
        num,ds,na,ea,lo,lf,le=hdr(TEX)
        with open(TEX,'rb') as f:
            f.seek(0x800); etab=f.read(num*28); f.seek(na); names=f.read(lf+400); f.seek(ea); exts=f.read(le+400)
        def gs(b,o): 
            e=b.find(b'\x00',o); return b[o:e].decode('ascii','replace')
        for i in range(num):
            a,b2,c,d,ln,m1,z=struct.unpack_from('<IIiiiii',etab,i*28)
            if gs(names,a)==name:
                with open(TEX,'rb') as f: f.seek(ds+d); return f.read(ln)
    buf=vp.read(e); rgb,a=S.dxt3_decode(buf,2048,2048); return a
patch_bytes=read_atlas(vp,"fnt_chinese","g_peg_pc")
common_bytes=read_atlas(None,"fnt_chinese")
pa=np.array(S.dxt3_decode(patch_bytes,2048,2048)[1]).astype(np.float32)/255
ca=np.array(S.dxt3_decode(common_bytes,2048,2048)[1]).astype(np.float32)/255
AT=2048;PITCH=31;COLS=66;X0=2;Y0=34;SX=48
def cell(atlas,idx):
    col=(idx-94)%COLS; row=(idx-94)//COLS
    x=X0+col*PITCH; y=Y0+row*PITCH
    m=atlas[y:y+SX, x:x+SX]
    m=np.clip(m,0,1)*255
    return np.stack([m,m,m],-1).astype(np.uint8)
import os
os.makedirs("F:/sr2-cn/_cellcheck",exist_ok=True)
for idx in [94,200,500,1000,2000]:
    pc=cell(pa,idx); cc=cell(ca,idx)
    combo=np.concatenate([pc,np.zeros((SX,SX//4,3),np.uint8),cc],1)
    Image.fromarray(combo).save(f"F:/sr2-cn/_cellcheck/cell{idx}_patchL_commonR.png")
print("saved cell images for indices 94,200,500,1000,2000 (patch LEFT, common RIGHT)")
