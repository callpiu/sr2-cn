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

pairs = [("律", 0x5F8B), ("延", 0x5EF6), ("三", 0x4E09), ("丈", 0x4E08),
         ("文", 0x6587), ("王", 0x738B)]
tiles = []
for ch, cp in pairs:
    i = CPS.index(cp)
    x, y = U[i], V[i]
    g = al[y:y+28, x:x+32]
    tiles.append(255 - g)
    tiles.append(np.full((28, 4), 128, np.uint8))
s = np.concatenate(tiles, axis=1)
img = Image.fromarray(s).resize((s.shape[1]*12, s.shape[0]*12), Image.NEAREST)
img.save(r"F:\sr2-cn\_juice_fix\cmp_glyph.png")
print("顺序: 律 延 三 丈 文 王  →", img.size)
for ch, cp in pairs:
    i = CPS.index(cp)
    print("  %s idx=%-5d slot=%-5d U=%4d V=%4d" % (ch, i, i+0x20, U[i], V[i]))
