import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N=struct.unpack_from("<i",vf3,0x08)[0]
U0=0xD0+N*16
U=list(struct.unpack_from("<%di"%N,vf3,U0))
nV=(len(vf3)-(U0+N*4))//4
V=list(struct.unpack_from("<%di"%nV,vf3,U0+N*4))
print("CPS[0..44]  =", repr("".join(chr(c) for c in CPS[:45])))
print("CPS[1055..1070] =", repr("".join(chr(c) for c in CPS[1055:1071])))
print("CPS[232..248]  =", repr("".join(chr(c) for c in CPS[232:249])))
print()
tiles=[]
for i in list(range(0,45)):
    x,y=U[i],V[i]
    g=al[y:y+31, x:x+31]
    tiles.append(255-g); tiles.append(np.full((31,1),120,np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(s).save(r"F:/sr2-cn/_juice_fix/head45.png")
print("写出 head45.png  (idx 0..44)")
