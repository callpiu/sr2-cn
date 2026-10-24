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
print("idx 1050..1060 对应字:", "".join(chr(CPS[i]) for i in range(1050,1061)))
print("idx 235..245 对应字:", "".join(chr(CPS[i]) for i in range(235,246)))
print("CPS.index(律=0x5F8B) =", CPS.index(0x5F8B), " → slot", CPS.index(0x5F8B)+0x20)
print("CPS.index(延=0x5EF6) =", CPS.index(0x5EF6), " → slot", CPS.index(0x5EF6)+0x20)
print("CPS.index(三=0x4E09) =", CPS.index(0x4E09), " → slot", CPS.index(0x4E09)+0x20)
print("CPS.index(丈=0x4E08) =", CPS.index(0x4E08), " → slot", CPS.index(0x4E08)+0x20)
print("CPS.index(文=0x6587) =", CPS.index(0x6587), " → slot", CPS.index(0x6587)+0x20)
print("CPS.index(辩=0x8FA9) =", CPS.index(0x8FA9), " → slot", CPS.index(0x8FA9)+0x20)
print("CPS.index(护=0x62A4) =", CPS.index(0x62A4), " → slot", CPS.index(0x62A4)+0x20)
print("CPS.index(师=0x5E08) =", CPS.index(0x5E08), " → slot", CPS.index(0x5E08)+0x20)
print("CPS.index(王=0x738B) =", CPS.index(0x738B), " → slot", CPS.index(0x738B)+0x20)
print()
# 正确方式: 28x31
order=[("辩",2506),("护",1222),("律",1089),("延",1057),("师",1013),
       ("三",271),("丈",270),("王",1796),("文",1371)]
tiles=[]
for ch,slot in order:
    i=slot-0x20; x,y=U[i],V[i]
    g=al[y:y+28, x:x+31]
    print("%s slot=%-5d idx=%-5d (%4d,%4d) 墨量=%d" % (ch,slot,i,x,y,int((g>32).sum())))
    tiles.append(255-g); tiles.append(np.full((28,3),160,np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(s).resize((s.shape[1]*10,s.shape[0]*10),Image.NEAREST).save(r"F:/sr2-cn/_juice_fix/glyph_ok.png")
print("\n顺序: "+" ".join(c for c,_ in order))
