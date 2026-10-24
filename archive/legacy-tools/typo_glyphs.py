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
# 把 律/延/丈/文 四个字的字形抠出来
tiles=[]; labels=[]
for ch in "律延丈文王":
    cp = ord(ch)
    i = CPS.index(cp)
    x,y = U[i], V[i]
    g = al[y:y+28, x:x+31]
    tiles.append(g); tiles.append(np.zeros((28,3),np.uint8)); labels.append("%s(slot%d)"%(ch,i+0x20))
s=np.concatenate(tiles,axis=1)
Image.fromarray(255-s).resize((s.shape[1]*8, s.shape[0]*8), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\typo_glyphs.png")
print("写出 typo_glyphs.png : %s" % " | ".join(labels))
print()
# 这些字形的墨迹，看是否正常
for ch in "律延丈文王":
    cp = ord(ch); i = CPS.index(cp); x,y = U[i], V[i]
    ink = int((al[y:y+28, x:x+31] > 32).sum())
    print("  %s idx %-5d slot %-5d (U=%4d,V=%4d) 墨量 %d" % (ch, i, i+0x20, x, y, ink))
