import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
# 官方原版三件套
vo = Vpp(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
cl = None; at = None
for e in vo.entries():
    if e['name']=='charlist_CH' and e.get('ext')=='txt': cl = vo.read(e)
    if e['name']=='fnt_chinese' and e.get('ext')=='g_peg_pc': at = vo.read(e)
vf = None
for e in vo.entries():
    if e['name']=='fnt_chinese' and e.get('ext')=='vf3_pc': vf = vo.read(e)
print("官方: charlist=%s 图集=%s vf3=%s" % (len(cl) if cl else None, len(at) if at else None, len(vf) if vf else None))
nums=[int(s) for s in cl.decode('utf-8','replace').replace('\r','').split('\n') if s.strip().isdigit()]
print("官方 charlist 条目:", len(nums), " 前5:", nums[:5])
N=struct.unpack_from('<I',vf,8)[0]; H=0xBC; uo=H+N*16
U=[struct.unpack_from('<I',vf,uo+i*4)[0] for i in range(N)]
V=[struct.unpack_from('<I',vf,uo+N*4+i*4)[0] for i in range(N)]
recs=[struct.unpack_from('<IIII',vf,H+i*16) for i in range(N)]
print("官方 vf3 N =", N)
_, A = dxt3_decode(at, 2048, 2048)
print("图集解码:", A.shape, A.dtype)
c2i={}
for i,cp in enumerate(nums): c2i.setdefault(chr(cp), i)
def render(chars, label):
    imgs=[]; idxs=[]
    for ch in chars:
        i = c2i.get(ch)
        if i is None: continue
        idxs.append(i)
        u,v = U[i], V[i]
        w,h = recs[i][0], recs[i][1]
        cell = A[v:v+ (h or 32), u:u+(w or 32)]
        imgs.append(cell)
    if imgs:
        mw=max(x.shape[1] for x in imgs)
        strip=np.hstack([np.pad(x,((2,2),(0,mw-x.shape[1]))) for x in imgs])
        Image.fromarray(strip).resize((strip.shape[1]*3, strip.shape[0]*3), Image.NEAREST).save(r"F:/sr2-cn/_DF_%s.png"%label)
        print("  %s -> idx=%s" % (label, idxs))
render("ABCDEabcde0123", "off_ascii")
render("的一是不了人我", "off_cjk")
print("\n→ 请看 _DF_off_ascii.png（应显示 ABCDEabcde0123）与 _DF_off_cjk.png")
