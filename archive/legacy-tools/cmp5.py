import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
# 拼一张对照图：idx 153,154,162,208 (屏幕乱码前4个) 与 善(idx 703)
idxs = [153,154,162,208,703]
tiles=[]
for i in idxs:
    x,y=U[i],V[i]
    g = al[y:y+28, x:x+31]
    tiles.append(g); tiles.append(np.zeros((28,3),np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(255-s).resize((s.shape[1]*8, s.shape[0]*8), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\cmp5.png")
print("写出 cmp5.png")
print("顺序: idx153(¹) | idx154(º) | idx162(Â) | idx208(ð) | idx703(善)")
print()
for i in idxs:
    print("  idx %-4d 字表说它是 %r (U+%04X)" % (i, chr(CPS[i]) if CPS[i]>0x20 else "空格", CPS[i]))
