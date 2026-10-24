import sys, struct, re
import numpy as np
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
from PIL import Image

game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")
TEX=game+"textures.vpp_pc"

def load_charlist(vp,name):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE'); 
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]
cl=load_charlist(vp,"charlist_CH")
cp2ci={cp:i for i,cp in enumerate(cl)}

AT=2048; PITCH=31; COLS=66; X0=2; Y0=34; CELLSZ=31

def decode_full(vp,name,ext):
    e=vp.find(name,ext); buf=vp.read(e)
    rgb,a=S.dxt3_decode(buf,AT,AT)
    return a.astype(np.float32)/255.0

# common atlas: targeted read
def open_vpp_header(path):
    with open(path,'rb') as f:
        d=f.read(5+0x14F+20)
    o=5+0x14F
    num,cs,lo,lf,le=struct.unpack_from('<iiiii',d,o)
    names_at=((0x800+lo)&0xFFFFF800)+0x800
    ext_at=((names_at+lf)&0xFFFFF800)+0x800
    data_start=((ext_at+le)&0xFFFFF800)+0x800
    return num,data_start,names_at,ext_at,lo,lf,le

num,ds,names_at,ext_at,lo,lf,le=open_vpp_header(TEX)
with open(TEX,'rb') as f:
    f.seek(0x800); etab=f.read(num*28)
    f.seek(names_at); names=f.read(lf+200)
    f.seek(ext_at); exts=f.read(le+200)
def getstr(base,off):
    e=base.find(b'\x00',off); return base[off:e].decode('ascii','replace')
target=None
for i in range(num):
    a,b,c,d,ln,m1,z=struct.unpack_from('<IIiiiii',etab,i*28)
    if getstr(names,a)=='fnt_chinese':
        target=(ds+d,ln); break
print("common atlas region:",target)
with open(TEX,'rb') as f:
    f.seek(target[0]); blob=f.read(target[1])
rgb,a=S.dxt3_decode(blob,AT,AT)
common_a=a.astype(np.float32)/255.0
patch_a=decode_full(vp,"fnt_chinese","g_peg_pc")
print("atlases decoded. patch",patch_a.shape,"common",common_a.shape)

def cell_mask(atlas,idx):
    if idx<94: return None
    col=(idx-94)%COLS; row=(idx-94)//COLS
    x=X0+col*PITCH; y=Y0+row*PITCH
    if y+CELLSZ>AT or x+CELLSZ>AT: return None
    m=atlas[y:y+CELLSZ, x:x+CELLSZ]
    ys,xs=np.where(m>0.05)
    if len(xs)<5: return None
    m=m[ys.min():ys.max()+1, xs.min():xs.max()+1]
    if m.shape[0]<3 or m.shape[1]<3: return None
    im=Image.fromarray((np.clip(m,0,1)*255).astype(np.uint8)).resize((40,40))
    return np.array(im).astype(np.float32)/255.0

patch_ref={}
for idx in range(94,len(cl)):
    m=cell_mask(patch_a,idx)
    if m is not None: patch_ref[idx]=m
print("patch ref cells:",len(patch_ref))

def best_match(tgt_ci):
    tgt=patch_ref.get(tgt_ci)
    if tgt is None: return None
    best=None;bestv=-1
    for idx in range(94,2838):
        m=cell_mask(common_a,idx)
        if m is None: continue
        a=tgt-tgt.mean(); b=m-m.mean()
        denom=np.sqrt((a*a).sum())*np.sqrt((b*b).sum())
        v=(a*b).sum()/denom if denom>1e-6 else -1
        if v>bestv: bestv=v;best=idx
    return best,bestv

exp={'任':371,'璨':1836,'偶':1035,'巧':422,'位':332,'雄':2667,'衡':2296,'伪':391,'该':1190}
print("\n-- VALIDATE (patch glyph of anchor -> common cell) --")
for ch in ['任','璨','偶','巧','位','雄','衡','伪','该']:
    ci=cp2ci[ord(ch)]; res=best_match(ci)
    if res is None: print(f"  {ch}: NO REF"); continue
    bi,bv=res
    print(f"  {ch}(patch ci={ci}) -> common cell {bi} (exp {exp[ch]}) ncc={bv:.3f}")
