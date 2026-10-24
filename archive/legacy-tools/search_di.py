"""穷举搜索：patch 图集里到底哪个 cell 是「弟」？

思路
    既然「图集索引 i 的字形 != charlist[i] 的字」，那必然存在一个置换。
    用 ASCII 区做锚点（ASCII 字形形状唯一可辨），标定「图集 cell 序号 -> 索引」的映射，
    再检验 CJK 区。

    更直接的办法：把整张图集按 cell 铺开成一张索引图，
    人工比对其中一小块，找出「弟」的真实 cell 序号。

    这里先做数值检测：
      1) ASCII 区：索引 0..94 的 cell，抠出来拼图（应显示 !"#$%...~）
      2) 若 ASCII 区正确，则问题只在 CJK 区的一部分
      3) 把 CJK 区 1030..1080 铺开，人工找「弟」
"""
import os, sys, struct
import numpy as np
from PIL import Image

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"
SRC = os.path.join(G, "patch.vpp_pc.v531_before_mirror.bak")

v = Vpp(SRC)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
vf3 = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N * 16
U = list(struct.unpack_from("<%di" % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)


def draw(idxs, path, cols=40):
    tiles = []
    for i in idxs:
        if not (0 <= i < N):
            tiles.append(np.zeros((28, 31), np.uint8))
            continue
        g = al[V[i]:V[i] + 28, U[i]:U[i] + 31]
        if g.shape != (28, 31):
            pad = np.zeros((28, 31), np.uint8)
            pad[:g.shape[0], :g.shape[1]] = g
            g = pad
        tiles.append(g)
    rows = []
    for r in range(0, len(tiles), cols):
        chunk = tiles[r:r + cols]
        row = []
        for g in chunk:
            row.append(g)
            row.append(np.full((28, 1), 200, np.uint8))
        while len(row) < cols * 2 - 1:
            row.append(np.zeros((28, 31), np.uint8))
            row.append(np.full((28, 1), 200, np.uint8))
        rows.append(np.concatenate(row[:cols * 2 - 1], axis=1))
    s = np.concatenate(rows, axis=0)
    sc = max(1, min(6, 1600 // max(1, s.shape[1] // 8)))
    Image.fromarray(255 - s).resize((s.shape[1] * 4, s.shape[0] * 4), Image.NEAREST).save(path)
    return s.shape


# 1) ASCII 区 0..94
sh = draw(list(range(0, 95)), os.path.join(OUT, "ascii_region.png"), 48)
print("1) ASCII 区 0..94 -> ascii_region.png %s" % (sh,))
print("   字表说应为: %s" % "".join(chr(cn[i]) for i in range(95)))
print()

# 2) CJK 区 1030..1085（应包含 弟）
sh = draw(list(range(1030, 1086)), os.path.join(OUT, "cjk_1030_1085.png"), 28)
print("2) 索引 1030..1085 -> cjk_1030_1085.png %s" % (sh,))
print("   字表说应为: %s" % "".join(chr(cn[i]) for i in range(1030, 1086)))
print()

# 3) 大范围搜索「弟」：把 900..1200 铺开
sh = draw(list(range(900, 1200)), os.path.join(OUT, "cjk_900_1200.png"), 50)
print("3) 索引 900..1200 -> cjk_900_1200.png %s（每行 50 个）" % (sh,))
print("   字表区间: %s ..." % "".join(chr(cn[i]) for i in range(900, 940)))
