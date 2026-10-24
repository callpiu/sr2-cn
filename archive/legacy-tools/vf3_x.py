# -*- coding: utf-8 -*-
"""核心验证：游戏渲染「律(idx1057)」时实际取到哪个 cell。
   逐一枚举 (图集, vf3) 组合，看哪一组能复现用户看到的 延/丈。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"
os.makedirs(OUT, exist_ok=True)

print("### 1. 所有 fnt_chinese 图集副本的哈希")
atlases = {}
for f, ext in [("patch.vpp_pc", "g_peg_pc"), ("textures.vpp_pc", "")]:
    v = Vpp(os.path.join(G, f))
    d = bytes(v.read(v.find("fnt_chinese", ext)))
    atlases[f] = d
    print("  %-18s ext=%-10r %9d bytes  md5=%s"
          % (f, ext, len(d), hashlib.md5(d).hexdigest()))
print("  相同? %s" % ("是" if atlases["patch.vpp_pc"] == atlases["textures.vpp_pc"]
                   else "★不同★"))

print("\n### 2. pegs.vpp_pc 的 fnt_chinese(94B) 内容")
v = Vpp(os.path.join(G, "pegs.vpp_pc"))
peg = bytes(v.read(v.find("fnt_chinese", "")))
print("  hex: %s" % peg.hex())

print("\n### 3. 两份 vf3 的 N 与 U/V")
vfs = {}
for f in ["patch.vpp_pc", "common.vpp_pc"]:
    v = Vpp(os.path.join(G, f))
    d = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
    vfs[f] = d
    N = struct.unpack_from("<i", d, 0x08)[0]
    print("  %-18s %7d B  N=%-5d 结构尾=0x%X EOF=0x%X %s"
          % (f, len(d), N, 0xBC + N * 16 + N * 8, len(d),
             "自洽" if 0xBC + N * 16 + N * 8 == len(d) else "★不自洽★"))

def uv(d, i):
    N = struct.unpack_from("<i", d, 0x08)[0]
    U0 = 0xBC + N * 16
    return (struct.unpack_from("<i", d, U0 + i * 4)[0],
            struct.unpack_from("<i", d, U0 + N * 4 + i * 4)[0])

print("\n### 4. 交叉渲染：每种 (图集 × vf3) 组合下关键 idx 的字形")
TARGETS = [(2474, "辩"), (1190, "护"), (1057, "律"), (1025, "延"),
           (981, "师"), (239, "三"), (238, "丈"), (1764, "王")]
CELL = 31

# 参考基准：ASCII 区（两表前 95 项都是 ASCII，若两图集一致则都能对齐）
dec = {f: dxt3_decode(b, 2048, 2048)[1] for f, b in atlases.items()}

for af, alpha in dec.items():
    for vf, d in vfs.items():
        N = struct.unpack_from("<i", d, 0x08)[0]
        tiles, labels = [], []
        for idx, ch in TARGETS:
            if idx >= N:
                continue
            u, v = uv(d, idx)
            if u + CELL > 2048 or v + CELL > 2048:
                continue
            g = alpha[v:v + CELL, u:u + CELL]
            tiles.append((g > 100).astype(np.uint8) * 255)
            labels.append("%d:%s" % (idx, ch))
        if not tiles:
            continue
        row = np.concatenate(
            [np.pad(t, ((3, 3), (3, 3)), constant_values=0) for t in tiles], axis=1)
        nm = "X_%s__%s.png" % (af.split(".")[0], vf.split(".")[0])
        Image.fromarray(row).resize((row.shape[1] * 4, row.shape[0] * 4),
                                    Image.NEAREST).save(os.path.join(OUT, nm))
        print("  %-34s %s" % (nm, " ".join(labels)))

print("\n### 5. ASCII 自检：图集前 45 格应渲染 ' !\"#$%&...'（若整体错位会很明显）")
for af, alpha in dec.items():
    d = vfs["patch.vpp_pc"]
    tiles = []
    for idx in range(45):
        u, v = uv(d, idx)
        tiles.append((alpha[v:v + CELL, u:u + CELL] > 100).astype(np.uint8) * 255)
    row = np.concatenate(
        [np.pad(t, ((2, 2), (2, 2)), constant_values=0) for t in tiles], axis=1)
    nm = "ASCII_%s.png" % af.split(".")[0]
    Image.fromarray(row).resize((row.shape[1] * 3, row.shape[0] * 3),
                                Image.NEAREST).save(os.path.join(OUT, nm))
    print("  已输出 %s  (期望: 空格 ! \" # $ % & ' ( ) * + , - . / 0 1 2 ...)" % nm)