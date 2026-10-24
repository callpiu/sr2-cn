# -*- coding: utf-8 -*-
"""像素级判定：idx 1057(律) 在两张图集里到底画的是什么。"""
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

def N(d): return struct.unpack_from("<i", d, 0x08)[0]
def uv(d, i):
    n = N(d); U0 = 0xBC + n * 16
    return (struct.unpack_from("<i", d, U0 + i * 4)[0],
            struct.unpack_from("<i", d, U0 + n * 4 + i * 4)[0])

print("### A. 两份 vf3 的 U/V 数组是否逐项相同（重叠 0..2794）")
pa, co = vfs["patch.vpp_pc"], vfs["common.vpp_pc"]
diff = [i for i in range(2795) if uv(pa, i) != uv(co, i)]
print("  U/V 不同的 idx 个数 = %d / 2795" % len(diff))
if diff:
    print("  前 20 个:", diff[:20])
    for i in diff[:10]:
        print("    idx %5d  patch=%s  common=%s" % (i, uv(pa, i), uv(co, i)))

print("\n### B. 两份 vf3 尾部 43 项（2795..2837）common 独有")
for i in range(2795, 2838):
    print("    idx %5d  common U/V = %s" % (i, uv(co, i)))

print("\n### C. 关键 idx 在两张图集上的字形（各自用 patch vf3 定位）")
TARGETS = [(2474, "辩"), (1190, "护"), (1057, "律"), (1025, "延"),
           (981, "师"), (239, "三"), (238, "丈"), (1764, "王")]
dec = {f: dxt3_decode(b, 2048, 2048)[1] for f, b in atl.items()}

rows = []
for f, alpha in dec.items():
    tiles = []
    for idx, ch in TARGETS:
        u, v = uv(pa, idx)
        tiles.append((alpha[v:v + CELL, u:u + CELL] > 100).astype(np.uint8) * 255)
    rows.append(np.concatenate(
        [np.pad(t, ((3, 3), (3, 3)), constant_values=0) for t in tiles], axis=1))
    print("  %-18s 已渲染 %d 字" % (f, len(tiles)))

grid = np.concatenate(rows, axis=0)
Image.fromarray(grid).resize((grid.shape[1] * 4, grid.shape[0] * 4),
                             Image.NEAREST).save(os.path.join(OUT, "atlas_cmp.png"))
print("  上排=patch.vpp_pc   下排=textures.vpp_pc")
print("  顺序: %s" % "  ".join("%d(%s)" % (i, c) for i, c in TARGETS))
print("  已输出 atlas_cmp.png")

print("\n### D. ASCII 自检（两图集各 45 格）")
rows = []
for f, alpha in dec.items():
    tiles = []
    for idx in range(45):
        u, v = uv(pa, idx)
        tiles.append((alpha[v:v + CELL, u:u + CELL] > 100).astype(np.uint8) * 255)
    rows.append(np.concatenate(
        [np.pad(t, ((2, 2), (2, 2)), constant_values=0) for t in tiles], axis=1))
    print("  %-18s OK" % f)
grid = np.concatenate(rows, axis=0)
Image.fromarray(grid).resize((grid.shape[1] * 3, grid.shape[0] * 3),
                             Image.NEAREST).save(os.path.join(OUT, "ascii_cmp.png"))
print("  已输出 ascii_cmp.png  期望上/下排都是: (空) ! \" # $ % & ' ( ) * + , - . / 0 1 2")