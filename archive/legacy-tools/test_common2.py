import os, sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"
# common vf3
vc = Vpp(os.path.join(G,"common.vpp_pc"))
vf3c = bytes(vc.read(vc.find("fnt_chinese","vf3_pc")))
Nc = struct.unpack_from("<i", vf3c, 0x08)[0]
U0c = 0xD0 + Nc*16
Uc = list(struct.unpack_from("<%di"%Nc, vf3c, U0c))
nVc=(len(vf3c)-(U0c+Nc*4))//4
Vc = list(struct.unpack_from("<%di"%nVc, vf3c, U0c+Nc*4)) + [0]*(Nc-nVc)
with open(os.path.join(G,"textures.vpp_pc"),"rb") as f:
    f.seek(85407184); _, al_c = dxt3_decode(f.read(4194304), 2048, 2048)
# patch 字表
vp = Vpp(os.path.join(G,"patch.vpp_pc.v531_before_mirror.bak"))
cn = [int(l) for l in vp.read(vp.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
slots = [1067, 454, 364, 2699, 2328, 403, 1868, 423, 1222]
print("common vf3 N=%d, 字表 %d 项" % (Nc, len(cn)))
print("字表读出: %s" % "".join(S[x] for x in slots))
print()
_, al_p = dxt3_decode(bytes(vp.read(vp.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3p = bytes(vp.read(vp.find("fnt_chinese","vf3_pc")))
Np = struct.unpack_from("<i", vf3p, 0x08)[0]
U0p = 0xD0 + Np*16
Up = list(struct.unpack_from("<%di"%Np, vf3p, U0p))
nVp=(len(vf3p)-(U0p+Np*4))//4
Vp = list(struct.unpack_from("<%di"%nVp, vf3p, U0p+Np*4)) + [0]*(Np-nVp)
def render(atlas,U,V,N,K,path):
    tiles=[]
    for x in slots:
        i = x-0x20+K
        if not (0<=i<N): return False
        g = atlas[V[i]:V[i]+28, U[i]:U[i]+31]
        if g.shape != (28,31):
            pad=np.zeros((28,31),np.uint8); pad[:g.shape[0],:g.shape[1]]=g; g=pad
        tiles.append(g); tiles.append(np.full((28,2),255,np.uint8))
    s=np.concatenate(tiles,axis=1)
    Image.fromarray(255-s).resize((s.shape[1]*8,s.shape[0]*8),Image.NEAREST).save(path)
    return True
for K in (0,-5,5,21):
    ok = render(al_c,Uc,Vc,Nc,K, os.path.join(OUT,"cmn_K%d.png"%K))
    print("common K=%+3d -> cmn_K%d.png  %s" % (K,K,"OK" if ok else "越界"))
for K in (0,5,-5):
    ok = render(al_p,Up,Vp,Np,K, os.path.join(OUT,"pch_K%d.png"%K))
    print("patch  K=%+3d -> pch_K%d.png   %s" % (K,K,"OK" if ok else "越界"))
print()
print("期望: 弟兄们需要你的保护")
