# -*- coding: utf-8 -*-
"""4 种(图集 × vf3)组合全对比，定位游戏实际在用哪一套的错位。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"
CELL = 31

atl = {}
for f, ext in [("patch.vpp_pc", "g_peg_pc"), ("textures.vpp_pc", "")]:
    v = Vpp(os.path.join(G, f))
    atl[f] = bytes(v.read(v.find("fnt_chinese", ext)))
vfs = {}
for f in ["patch.vpp_pc", "common.vpp_pc"]:
    v = Vpp(os.path.join(G, f))
    vfs[f] = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
vpr = Vpp(r"F:\sr2-cn\pristine\patch.vpp_pc")
cps_patch = [int(l) for l in
             vpr.read(vpr.find("charlist_CH", "txt")).decode("utf-8").split("\n")
             if l.strip().isdigit()]
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps_orig = [int(l) for l in
            v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
            if l.strip().isdigit()]
print("现役charlist %d 项 / 原厂 %d 项" % (len(cps_orig), len(cps_patch)))

def N(d): return struct.unpack_from("<i", d, 0x08)[0]
def uv(d, i):
    n = N(d); U0 = 0xBC + n * 16
    return (struct.unpack_from("<i", d, U0 + i * 4)[0],
            struct.unpack_from("<i", d, U0 + n * 4 + i * 4)[0])

dec = {f: dxt3_decode(b, 2048, 2048)[1] for f, b in atl.items()}
TARGETS = [(2474, "辩"), (1190, "护"), (1057, "律"), (1025, "延"),
           (981, "师"), (239, "三"), (238, "丈"), (1764, "王")]
labels = "  ".join("%d(%s)" % (i, c) for i, c in TARGETS)

blocks = []
for af in ["patch.vpp_pc", "textures.vpp_pc"]:
    for vf in ["patch.vpp_pc", "common.vpp_pc"]:
        alpha = dec[af]; d = vfs[vf]
        tiles = []
        for idx, ch in TARGETS:
            u, v = uv(d, idx)
            if u + CELL > 2048 or v + CELL > 2048:
                tiles.append(np.zeros((CELL, CELL), np.uint8)); continue
            tiles.append((alpha[v:v + CELL, u:u + CELL] > 100).astype(np.uint8) * 255)
        rows = [np.concatenate([np.pad(t, ((3, 3), (3, 3)), constant_values=0)
                               for t in tiles], axis=1)]
        # 下面加 ASCII 自检条
        at = []
        for idx in range(45):
            u, v = uv(d, idx)
            at.append((alpha[v:v + CELL, u:u + CELL] > 100).astype(np.uint8) * 255
                      if u + CELL <= 2048 and v + CELL <= 2048
                      else np.zeros((CELL, CELL), np.uint8))
        arow = np.concatenate([np.pad(t, ((2, 2), (2, 2)), constant_values=0)
                               for t in at], axis=1)
        wmax = rows[0].shape[1]
        if arow.shape[1] > wmax:                # ASCII 条更宽 -> 裁到同宽
            arow = arow[:, :wmax]
        else:
            arow = np.pad(arow, ((0, 0), (0, wmax - arow.shape[1])),
                          constant_values=0)
        rows.append(arow)
        blocks.append((af, vf, np.concatenate(rows, axis=0)))
        print("  %-18s x %-18s  ->  已渲染" % (af, vf))

W = max(b[2].shape[1] for b in blocks)
padded = [np.pad(b[2], ((0, 6), (0, W - b[2].shape[1])), constant_values=0)
          for b in blocks]
grid = np.concatenate(padded, axis=0)
Image.fromarray(grid).save(os.path.join(OUT, "four_way.png"))
print("\n图集 x vf3 = 4 组，自上而下：")
for i, (af, vf, _) in enumerate(blocks):
    print("  第%d行  %s  x  %s" % (i + 1, af, vf))
print("每组上排=%s" % labels)
print("每组下排=ASCII 0..44 自检(期望: 空格!\"#$%&'()*+,-./0123)")
print("已输出 four_way.png")