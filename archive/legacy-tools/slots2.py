import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
names = [("律",1089),("延",1057),("文",1371),("丈",270),("王",1796),("师",1013),("辩",2506),("护",1222)]
tiles=[]
print("%-4s %-8s %-6s %-8s %s" % ("字","slot","索引","图集(U,V)","墨量"))
for ch, slot in names:
    i = slot - 0x20
    x,y = U[i], V[i]
    g = al[y:y+28, x:x+31]
    ink = int((g>32).sum())
    tiles.append(g); tiles.append(np.zeros((28,2),np.uint8))
    print("%-4s %-8d %-6d (%4d,%4d) %d" % (ch, slot, i, x, y, ink))
s=np.concatenate(tiles,axis=1)
Image.fromarray(255-s).resize((s.shape[1]*9,s.shape[0]*9),Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\slots.png")
print()
print("写出 slots.png")
