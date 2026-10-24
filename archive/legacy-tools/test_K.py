import os, sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G,"patch.vpp_pc.v531_before_mirror.bak")
v = Vpp(SRC)
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4)) + [0]*(N-nV)
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
slots = [1067, 454, 364, 2699, 2328, 403, 1868, 423, 1222]
print("字表读出: %s" % "".join(S[x] for x in slots))
print()
for K in (0, 5, 21, -5):
    tiles = []
    ok = True
    for x in slots:
        i = x - 0x20 + K
        if not (0 <= i < N): ok = False; break
        g = al[V[i]:V[i]+28, U[i]:U[i]+31]
        if g.shape != (28,31):
            pad = np.zeros((28,31),np.uint8); pad[:g.shape[0],:g.shape[1]] = g; g = pad
        tiles.append(g); tiles.append(np.full((28,2),255,np.uint8))
    if ok:
        s = np.concatenate(tiles, axis=1)
        Image.fromarray(255-s).resize((s.shape[1]*8, s.shape[0]*8), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\K%s.png" % str(K).replace("-","m"))
        print("  偏移 %+3d -> K%s.png" % (K, str(K).replace("-","m")))
print()
print("期望显示: 弟兄们需要你的保护")
