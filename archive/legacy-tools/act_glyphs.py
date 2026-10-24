import os, sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4)) + [0]*(N-nV)
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
# 用 V 的格数推断网格
print("N=%d, U 范围 %d..%d, V 范围 %d..%d" % (N, min(U), max(U), min(V), max(V)))
# 行分组
rows = {}
for i in range(N):
    rows.setdefault(V[i], []).append(i)
print("不同 V 值（行）数: %d" % len(rows))
vs = sorted(rows)
print("前 6 行 V: %s  每行字数: %s" % (vs[:6], [len(rows[x]) for x in vs[:6]]))
print()
# 抠出目标索引的字形
targets = ["弟","兄","们","需","要","你","的","保","护"]
tiles = []
for ch in targets:
    i = CPS.index(ord(ch))
    x, y = U[i], V[i]
    g = al[y:y+28, x:x+31]
    if g.shape != (28,31):
        pad = np.zeros((28,31), np.uint8); pad[:g.shape[0],:g.shape[1]] = g; g = pad
    tiles.append(g); tiles.append(np.full((28,2), 255, np.uint8))
s = np.concatenate(tiles, axis=1)
Image.fromarray(255-s).resize((s.shape[1]*7, s.shape[0]*7), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\act_glyphs.png")
print("写出 act_glyphs.png")
print("顺序: %s" % " ".join(targets))
print("索引: %s" % [CPS.index(ord(c)) for c in targets])
print("U: %s" % [U[CPS.index(ord(c))] for c in targets])
print("V: %s" % [V[CPS.index(ord(c))] for c in targets])
