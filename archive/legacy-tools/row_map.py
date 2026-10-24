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
# 用「行」来展示图集：固定 V 一行里，按 U 排序 -> 图集顺序
rows = {}
for i in range(N):
    rows.setdefault(V[i], []).append(i)
vs = sorted(rows)
# 取一整行（65 个）做对比图
row_v = vs[10]      # 选一行
idxs = sorted(rows[row_v], key=lambda i: U[i])
print("行 V=%d, 共 %d 个索引, 索引范围 %d..%d" % (row_v, len(idxs), idxs[0], idxs[-1]))
print("  该行索引: %s" % idxs[:20])
print("  字表说这些索引是: %s" % "".join(chr(CPS[i]) for i in idxs[:20]))
print()
# 抠图 + 标注
CELL_W, CELL_H = 31, 31
tiles = []
for i in idxs[:40]:
    x, y = U[i], V[i]
    g = al[y:y+CELL_H-3, x:x+CELL_W]
    if g.shape != (CELL_H-3, CELL_W):
        pad = np.zeros((CELL_H-3, CELL_W), np.uint8); pad[:g.shape[0],:g.shape[1]] = g; g = pad
    tiles.append(g); tiles.append(np.full((CELL_H-3, 2), 255, np.uint8))
s = np.concatenate(tiles, axis=1)
Image.fromarray(255-s).resize((s.shape[1]*6, s.shape[0]*6), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\row_map.png")
print("写出 row_map.png（该行前 40 个字，按 U 排序）")
print("  索引: %s" % idxs[:40])
print("  字表: %s" % "".join(chr(CPS[i]) for i in idxs[:40]))
