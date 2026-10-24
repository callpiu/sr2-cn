"""数值搜索：patch 图集的字形序列与 charlist_CH 之间的偏移是多少？

思路
    图集里每个 cell 放着一个字形。若图集顺序 = charlist 顺序 + k，
    那么「用索引 i+k 去抠图」得到的就是 charlist[i] 的字。

做法
    用「像素指纹」而不是肉眼：对每个候选偏移 k，把 probe 里每个字的
    预期字形（在某个参照图集中抠出）与候选位置的字形做匹配。

    但更简单可靠的办法：**利用 ASCII 区**。
    charlist 前 95 项是 ASCII 0x20..0x7E。ASCII 字形形状固定，
    我们可以用「已确认正确」的参照来标定。

    不依赖参照的话，还有一个自洽性检验：
    同一行（相同 V）内，索引应当连续且与 U 同步。
    检查 (索引, U, V) 三元组是否满足「按索引排序后 U 单调」。

本脚本做三件事：
  1. 检查索引→(U,V) 是否单调（是否图集按索引顺序排布）
  2. 用 ASCII 字形做锚点：ASCII 形状可人工辨认
  3. 输出候选偏移下 probe 字的拼图，供肉眼一次判定
"""
import os, sys, struct, collections
import numpy as np
from PIL import Image

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
vf3 = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
WIDTH, HEIGHT, RENDERH, CSP = struct.unpack_from("<hhh", vf3, 0x10) + (struct.unpack_from("<h", vf3, 0x1C)[0],)
U0 = 0xD0 + N * 16
U = list(struct.unpack_from("<%di" % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)

print("N=%d Width=%d Height=%d RenderH=%d CharSpacing=%d" % (N, WIDTH, HEIGHT, RENDERH, CSP))
print()

# 1) 索引排序后 (U,V) 是否单调（说明图集按索引顺序填）
rows = collections.defaultdict(list)
for i in range(N):
    rows[V[i]].append(i)
vs = sorted(rows)
seq = []
for vv in vs:
    for i in sorted(rows[vv], key=lambda k: U[k]):
        seq.append(i)
print("1) 图集物理顺序 vs 索引顺序")
print("   物理顺序前 20 个索引: %s" % seq[:20])
print("   是否等于 0..N-1: %s" % (seq[:20] == list(range(20))))
# 找物理顺序与索引的偏差
dev = [seq[k] - k for k in range(0, N, 200)]
print("   (物理序号 - 索引) 采样: %s" % dev)
print()

# 2) ASCII 锚点：抠出索引 0..15 的 ASCII，看读出来是什么
print("2) ASCII 锚点")
tiles = []
for i in range(0, 32):
    x, y = U[i], V[i]
    g = al[y:y + 28, x:x + 31]
    if g.shape != (28, 31):
        pad = np.zeros((28, 31), np.uint8); pad[:g.shape[0], :g.shape[1]] = g; g = pad
    tiles.append(g); tiles.append(np.full((28, 2), 255, np.uint8))
s = np.concatenate(tiles, axis=1)
Image.fromarray(255 - s).resize((s.shape[1] * 8, s.shape[0] * 8), Image.NEAREST).save(os.path.join(OUT, "ascii_anchor.png"))
print("   写出 ascii_anchor.png（索引 0..31，字表说它们是: %s）" % "".join(chr(cn[i]) for i in range(32)))
print()

# 3) 候选偏移拼图：probe 里的字，用 索引+k 抠
probe = "一二三四五六七八九十"
pidx = [cn.index(ord(c)) for c in probe]
print("3) 候选偏移拼图")
print("   probe=%s  索引=%s" % (probe, pidx))
rows_img = []
for k in (-10, -5, -3, -1, 0, 1, 3, 5, 10):
    tiles = []
    ok = True
    for i in pidx:
        j = i + k
        if not (0 <= j < N):
            ok = False; break
        x, y = U[j], V[j]
        g = al[y:y + 28, x:x + 31]
        if g.shape != (28, 31):
            pad = np.zeros((28, 31), np.uint8); pad[:g.shape[0], :g.shape[1]] = g; g = pad
        tiles.append(g); tiles.append(np.full((28, 3), 128, np.uint8))
    if ok:
        rows_img.append(np.concatenate(tiles, axis=1))
if rows_img:
    W = max(r.shape[1] for r in rows_img)
    padded = []
    for r in rows_img:
        if r.shape[1] < W:
            r = np.pad(r, ((0, 0), (0, W - r.shape[1])), constant_values=200)
        padded.append(r)
        padded.append(np.full((8, W), 100, np.uint8))
    s = np.concatenate(padded, axis=0)
    Image.fromarray(255 - s).resize((s.shape[1] * 6, s.shape[0] * 6), Image.NEAREST).save(os.path.join(OUT, "offset_candidates.png"))
    print("   写出 offset_candidates.png，偏移依次为: %s" % [-10, -5, -3, -1, 0, 1, 3, 5, 10])
    print("   期望每一行都显示: %s" % probe)
