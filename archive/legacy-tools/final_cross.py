"""最终交叉验证：图集索引 <-> 用户报告的乱码字

已知
  - v531/v532 数据里 REC1 的槽位（含 [format] 标签）：
    [91,102,111,114,109,97,116,93, 91,99,111,108,111,114,58,103,114,101,101,110,93,
     1067,454,364, 91,47,102,111,114,109,97,116,93, 2699,2328,403,1868,423,1222]
    -> [format][color:green]弟兄们[/format]需要你的保护

  - 用户看到（REC1 中国字部分）: 任璨偶巧位雄衡任璨伪该

本脚本
  1. 在 v531 上重新取 REC1 的槽位（v531 是干净数据）
  2. 用「图集索引」= 槽位 - 0x20，抠出字形，逐字与用户报告对照
  3. 同时用 charlist 解码，列出 (槽位, 字表字, 图集字形索引)
"""
import os, sys, struct
import numpy as np
from PIL import Image

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"
H1 = 0x84F287ED

# 用 v531（干净、图集对齐）
SRC = os.path.join(G, "patch.vpp_pc.v531_before_mirror.bak")
v = Vpp(SRC)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
vf3 = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N * 16
U = list(struct.unpack_from("<%di" % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)

d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)
rec = None
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    cands = []
    for base in (0, 4):
        for endian in ("<", ">"):
            if off + base + 4 > len(d):
                continue
            v0, = struct.unpack_from(endian + "H", d, off + base)
            v1, = struct.unpack_from(endian + "H", d, off + base + 2)
            cands += [(v0 << 16) | v1, (v1 << 16) | v0]
    if H1 not in cands:
        continue
    u, end = read_units(d, off + 8)
    rec = (off, [x for x, _ in u])
    break

off, vals = rec
print("REC1 @%d, %d 槽位" % (off, len(vals)))
print("槽位: %s" % vals)
print("字表解码: %s" % "".join(S.get(x, "·") for x in vals))
print()

# 用户报告的乱码（REC1 部分）
USER = "任璨偶巧位雄衡任璨伪该"
print("用户报告: %s" % USER)
print()

# 逐字：槽位 -> 字表字 -> 图集该索引的字形
print("=== 逐字对照（用图集索引 = 槽位-0x20 抠字形）===")
print("  %-4s %-6s %-8s %s" % ("位置", "槽位", "字表字", "图集(U,V)"))
tiles = []
chars = []
for k, x in enumerate(vals):
    if x < 0x100:
        continue
    i = x - 0x20
    if not (0 <= i < N):
        continue
    ch = S.get(x, "?")
    chars.append((k, x, ch, U[i], V[i]))
print("  —— 非 ASCII 部分 %d 字 ——" % len(chars))
for k, x, ch, ux, vy in chars:
    print("  %-4d %-6d %-8s (%4d,%4d)" % (k, x, ch, ux, vy))
print()
print("  字表读出的中文: %s" % "".join(c[2] for c in chars))
print()

# 出图：把这一串字形抠出来
tiles = []
for k, x, ch, ux, vy in chars:
    g = al[vy:vy + 28, ux:ux + 31]
    if g.shape != (28, 31):
        pad = np.zeros((28, 31), np.uint8)
        pad[:g.shape[0], :g.shape[1]] = g
        g = pad
    tiles.append(g)
    tiles.append(np.full((28, 2), 255, np.uint8))
s = np.concatenate(tiles, axis=1)
Image.fromarray(255 - s).resize((s.shape[1] * 8, s.shape[0] * 8), Image.NEAREST).save(
    os.path.join(OUT, "rec1_atlas.png"))
print("写出 rec1_atlas.png（字表读出的中文对应的图集字形）")
print("  应为: %s" % "".join(c[2] for c in chars))
