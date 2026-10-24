"""系统性搜索：找出 HUD 渲染活动串时用到的映射。

目标
    用户在屏幕上看到的（REC1 中文字部分）: 任璨偶巧位雄衡...
    数据里的（charlist 解码）:            弟兄们需要你的保护

    数据槽位: [1067, 454, 364, 2699, 2328, 403, 1868, 423, 1222]

如果 HUD 用的是 shape 索引 = 槽位 - 0x20 + K（某个常量 K），
那我用 (槽位-0x20+K) 抠 patch 图集，就应该得到用户看到的字。

本脚本把 K 从 -64 扫到 +64，报告每个 K 下抠出的字。

另外再试两种变体：
   变体 A: 索引 = 槽位 - 0x20 + K      （槽位基准）
   变体 B: 索引 = 槽位 + K             （直接用槽位当索引）
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
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N * 16
U = list(struct.unpack_from("<%di" % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)

slots = [1067, 454, 364, 2699, 2328, 403, 1868, 423, 1222]
USER = "任璨偶巧位雄衡任璨伪该"
print("槽位: %s" % slots)
print("用户看到: %s" % USER)
print()

# 出图：把 K=-64..64 的每个映射铺成一行，方便一次看出哪个对
def grab(i):
    if not (0 <= i < N):
        return np.zeros((28, 31), np.uint8)
    g = al[V[i]:V[i] + 28, U[i]:U[i] + 31]
    if g.shape != (28, 31):
        pad = np.zeros((28, 31), np.uint8)
        pad[:g.shape[0], :g.shape[1]] = g
        g = pad
    return g


Ks = list(range(-64, 65, 4))
rows = []
for variant in ("minus0x20", "raw"):
    base = [x - 0x20 for x in slots] if variant == "minus0x20" else list(slots)
    for K in Ks:
        tiles = []
        for bs in base:
            tiles.append(grab(bs + K))
            tiles.append(np.full((28, 1), 200, np.uint8))
        rows.append((variant, K, np.concatenate(tiles[:-1], axis=1)))

# 拼成一张大图
maxw = max(r[2].shape[1] for r in rows)
imgs = []
labels = []
for variant, K, r in rows:
    if r.shape[1] < maxw:
        r = np.pad(r, ((0, 0), (0, maxw - r.shape[1])), constant_values=255)
    imgs.append(r)
    imgs.append(np.full((4, maxw), 120, np.uint8))
    labels.append("%s K=%+d" % (variant, K))
s = np.concatenate(imgs, axis=0)
Image.fromarray(255 - s).resize((s.shape[1] * 5, s.shape[0] * 5), Image.NEAREST).save(
    os.path.join(OUT, "K_sweep.png"))
print("写出 K_sweep.png")
print("  行顺序（每行 9 个字形）:")
for i, lab in enumerate(labels):
    print("    %2d: %s" % (i, lab))
