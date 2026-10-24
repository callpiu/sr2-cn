# -*- coding: utf-8 -*-
"""验证：游戏实际用的 vf3 到底是 patch 的 2795 版还是 common 的 2838 版。
   方法：用两份 vf3 的 U/V 数组分别渲染 idx 1057(律)/1025(延)/239(三)/238(丈)，
   看哪份 vf3 + 哪张图集能复现用户看到的「延」「丈」。
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

print("### 1. 两张图集是否同一份？")
imgs = {}
for tag, p in [(r"patch.vpp_pc", os.path.join(G, "patch.vpp_pc")),
               (r"textures.vpp_pc", os.path.join(G, "textures.vpp_pc"))]:
    v = Vpp(p)
    d = bytes(v.read(v.find("fnt_chinese", "g_peg_pc")))
    imgs[tag] = d
    print("  %-20s %9d bytes  md5=%s" % (tag, len(d),
          hashlib.md5(d).hexdigest()))
same = imgs[r"patch.vpp_pc"] == imgs[r"textures.vpp_pc"]
print("  两张图集字节相同? %s" % ("是" if same else "★不同★"))

print("\n### 2. 两份 vf3 的结构")
vfs = {}
for tag, p in [(r"patch.vpp_pc", os.path.join(G, "patch.vpp_pc")),
               (r"common.vpp_pc", os.path.join(G, "common.vpp_pc"))]:
    v = Vpp(p)
    d = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
    vfs[tag] = d
    N = struct.unpack_from("<i", d, 0x08)[0]
    U0 = 0xBC + N * 16
    V0 = U0 + N * 4
    print("  %-20s %7d bytes  N=%d  U0=0x%X  V0=0x%X  V尾=0x%X  EOF=0x%X"
          % (tag, len(d), N, U0, V0, V0 + N * 4, len(d)))
    assert V0 + N * 4 == len(d), "结构不自洽!"

print("\n### 3. 两份 vf3 的 U/V 是否相同（重叠范围）")
def uv(d, i):
    N = struct.unpack_from("<i", d, 0x08)[0]
    U0 = 0xBC + N * 16
    return (struct.unpack_from("<i", d, U0 + i * 4)[0],
            struct.unpack_from("<i", d, U0 + N * 4 + i * 4)[0])

pa, co = vfs[r"patch.vpp_pc"], vfs[r"common.vpp_pc"]
for i in [0, 1, 238, 239, 981, 1025, 1057, 1190, 1764, 2474]:
    ua, va = uv(pa, i)
    uc, vc = uv(co, i)
    print("  idx %5d  patch(U=%-5d V=%-5d)   common(U=%-5d V=%-5d)  %s"
          % (i, ua, va, uc, vc, "同" if (ua, va) == (uc, vc) else "★不同★"))

print("\n### 4. 解码图集，按两份 vf3 分别渲染关键 idx")
blk, alpha = dxt3_decode(imgs[r"patch.vpp_pc"], 2048, 2048)
CELL = 31
targets = [(1025, "延"), (1057, "律"), (238, "丈"), (239, "三"),
           (2474, "辩"), (981, "师")]

# 判断某 cell 里画的是不是给定汉字：用「墨迹密度 + 与已知参考比对」不可靠，
# 改为输出图像供人工核对。先输出两张对照图。
def dump(name, getter):
    tiles = []
    for idx, ch in targets:
        u, v = getter(idx)
        g = alpha[v:v + CELL, u:u + CELL]
        g = (g > 100).astype(np.uint8) * 255
        tiles.append(g)
    row = np.concatenate([np.pad(t, ((2, 2), (2, 2)), constant_values=0)
                          for t in tiles], axis=1)
    from PIL import Image
    Image.fromarray(row).resize((row.shape[1] * 5, row.shape[0] * 5),
                                Image.NEAREST).save(
        r"F:\sr2-cn\_juice_fix\%s.png" % name)
    print("  已输出 %s.png   顺序: %s" % (
        name, " ".join("%d=%s" % (i, c) for i, c in targets)))

dump("vf3_patch", lambda i: uv(pa, i))
dump("vf3_common", lambda i: uv(co, i))
print("\n  两行图若有差异 -> 游戏用的不是我之前那份 vf3")