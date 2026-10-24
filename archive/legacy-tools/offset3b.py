import os, sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4)) + [0]*(N-nV)
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
S = set(cn)
probe = "".join(c for c in "一二三四五六七八九十日月山口中人大上下左右你我他" if ord(c) in S)
pidx = [cn.index(ord(c)) for c in probe]
print("probe=%s" % probe)
print("索引=%s" % pidx)
print()
def render(k, path):
    tiles = []
    for i in pidx:
        j = i + k
        if not (0 <= j < N): return False
        x, y = U[j], V[j]
        g = al[y:y+28, x:x+31]
        if g.shape != (28,31):
            pad = np.zeros((28,31),np.uint8); pad[:g.shape[0],:g.shape[1]] = g; g = pad
        tiles.append(g); tiles.append(np.full((28,3),128,np.uint8))
    s = np.concatenate(tiles, axis=1)
    Image.fromarray(255-s).resize((s.shape[1]*7, s.shape[0]*7), Image.NEAREST).save(path)
    return True
for k, nm in ((-5,"m5"),(0,"p0"),(5,"p5")):
    ok = render(k, r"F:\sr2-cn\_juice_fix\off_%s.png" % nm)
    print("  偏移 %+d -> off_%s.png  %s" % (k, nm, "OK" if ok else "越界"))
print()
print("期望: %s" % probe)
