import sys, struct, re
import numpy as np
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
from PIL import Image
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc"); TEX=game+"textures.vpp_pc"
def load_charlist(vp,name):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE'); 
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]
cl=load_charlist(vp,"charlist_CH"); cp2ci={cp:i for i,cp in enumerate(cl)}
def hdr(path):
    with open(path,'rb') as f: d=f.read(5+0x14F+20)
    o=5+0x14F; num,cs,lo,lf,le=struct.unpack_from('<iiiii',d,o)
    names_at=((0x800+lo)&0xFFFFF800)+0x800; ext_at=((names_at+lf)&0xFFFFF800)+0x800
    data_start=((ext_at+le)&0xFFFFF800)+0x800
    return num,data_start,names_at,ext_at,lo,lf,le
num,ds,na,ea,lo,lf,le=hdr(TEX)
with open(TEX,'rb') as f:
    f.seek(0x800); etab=f.read(num*28); f.seek(na); names=f.read(lf+400); f.seek(ea); exts=f.read(le+400)
def gs(b,o):
    e=b.find(b'\x00',o); return b[o:e].decode('ascii','replace')
cb=None
for i in range(num):
    a,b2,c,d,ln,m1,z=struct.unpack_from('<IIiiiii',etab,i*28)
    if gs(names,a)=='fnt_chinese':
        with open(TEX,'rb') as f: f.seek(ds+d); cb=f.read(ln)
pa=np.array(S.dxt3_decode(vp.read(vp.find("fnt_chinese","g_peg_pc")),2048,2048)[1]).astype(np.float32)/255
ca=np.array(S.dxt3_decode(cb,2048,2048)[1]).astype(np.float32)/255
AT=2048; COLS=66
def cell(atlas,idx,pitch,cellw=26,x0=2,y0=34):
    if idx<94: return None
    col=(idx-94)%COLS; row=(idx-94)//COLS
    x=x0+col*pitch; y=y0+row*pitch
    if y+cellw>AT or x+cellw>AT: return None
    m=atlas[y:y+cellw, x:x+cellw]
    ys,xs=np.where(m>0.08)
    if len(xs)<6: return None
    m=m[ys.min():ys.max()+1, xs.min():xs.max()+1]
    if m.shape[0]<4 or m.shape[1]<4: return None
    im=Image.fromarray((np.clip(m,0,1)*255).astype(np.uint8)).resize((44,44))
    return np.array(im).astype(np.float32)/255
patch_ref={}
for idx in range(94,len(cl)):
    m=cell(pa,idx,31)
    if m is not None: patch_ref[idx]=m
def best_match(tgt_ci,pitch):
    tgt=patch_ref.get(tgt_ci)
    if tgt is None: return None
    best=None;bestv=-1
    for idx in range(94,2838):
        m=cell(ca,idx,pitch)
        if m is None: continue
        a=tgt-tgt.mean(); b=m-m.mean()
        denom=np.sqrt((a*a).sum())*np.sqrt((b*b).sum())
        v=(a*b).sum()/denom if denom>1e-6 else -1
        if v>bestv: bestv=v;best=idx
    return best,bestv
exp={'任':371,'璨':1836,'偶':1035,'巧':422,'位':332,'雄':2667,'衡':2296,'伪':391,'该':1190}
print("-- common grid pitch=30 --")
for ch in ['任','璨','偶','巧','位','雄','衡','伪','该']:
    ci=cp2ci[ord(ch)]; res=best_match(ci,30)
    if res is None: print(f"  {ch}: NO REF"); continue
    bi,bv=res
    flag="OK" if bi==exp[ch] else "??"
    print(f"  {ch}(patch ci={ci}) -> common cell {bi} (exp {exp[ch]}) ncc={bv:.3f} {flag}")
