import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
d = bytes(v.read(v.find("fnt_chinese","g_peg_pc")))
rgb, al = dxt3_decode(d, 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i",vf3,0x08)[0]
U0 = 0xD0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
WID=[struct.unpack_from("<h",vf3,0xD0+i*16)[0] for i in range(N)]
idx={}
for i,cp in enumerate(CPS):
    if 0x20<=cp<=0x7E: idx.setdefault(cp,i)

print("=== 用正确的 DXT3 解码，检查 JUICED 各字母 ===")
for ch in "JUICED":
    i=idx[ord(ch)]; x,y=U[i],V[i]
    m = al[y:y+28, x:x+17] > 32
    ys=np.nonzero(m.any(axis=1))[0]; xs=np.nonzero(m.any(axis=0))[0]
    print("  %s 索引%3d (U=%4d,V=%3d,w=%2d) 墨量%3d 行%s 列%s" % (
        ch,i,x,y,WID[i],int(m.sum()),
        str((int(ys.min()),int(ys.max()))) if len(ys) else "无",
        str((int(xs.min()),int(xs.max()))) if len(xs) else "无"))
print()
# 把 ASCII 前 3 行（按 vf3 坐标）渲染出来
tiles=[]
for k in range(95):
    i=k
    x,y=U[i],V[i]
    t=al[y:y+30, x:x+32]
    if t.shape!=(30,32):
        p=np.zeros((30,32),np.uint8); p[:t.shape[0],:t.shape[1]]=t; t=p
    tiles.append(t); tiles.append(np.zeros((30,2),np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(255-s).resize((s.shape[1]*4, s.shape[0]*4), Image.NEAREST).save(os.path.join(W,"_juice_fix","ascii_correct.png"))
print("写出 ascii_correct.png (按 vf3 坐标的正确 DXT3 视图)")
