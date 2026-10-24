# -*- coding: utf-8 -*-
"""渲染全字表成图片，用于肉眼核对字形是否错位。

★ 记忆里的坐标：vf3 patch 版 N=2795，U @0xAF6C、V @0xDB18，各 N 项，cell=31px。
  自检：渲染 idx 0..44 应得 ` !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKL`
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
import numpy as np
from PIL import Image
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

OUT = r"F:/sr2-cn/_字体核对"
os.makedirs(OUT, exist_ok=True)
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))

CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
print("字表 N =", N)

vf3 = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
n3 = struct.unpack_from("<i", vf3, 8)[0]
print("vf3 内 NumCharacters =", n3, " 文件大小 =", len(vf3))

U0 = 0xAF6C
V0 = 0xDB18
assert n3 == N == 2795, "N 不一致"
assert U0 + N * 4 <= len(vf3), "U 数组越界"
assert V0 + N * 4 <= len(vf3), "V 数组越界"
U = list(struct.unpack_from("<%di" % N, vf3, U0))
V = list(struct.unpack_from("<%di" % N, vf3, V0))
print("U[0:8] =", U[:8])
print("V[0:8] =", V[:8])

# ASCII 区自检：按记忆，ASCII 在图集 row 0，cell 31px
# 先看 idx 0 渲染出什么
_, alpha = sr2lib.dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))),
                               2048, 2048)
print("图集 alpha 形状", alpha.shape)

COLS, CELL = 66, 31


def render(idx):
    x, y = U[idx], V[idx]
    g = alpha[y:y + 28, x:x + CELL]
    if g.shape[0] < 28 or g.shape[1] < CELL:
        return np.zeros((28, CELL), np.uint8)
    return g


# ASCII 自检：idx 0..44 应该是  !"#$%&'()*+,-./0123456789:;<=>?@ABCD...
strip = "".join(chr(CPS[i]) for i in range(0, 60))
print("字表前60字符:", repr(strip))


def save_range(name, idxs):
    rows = (len(idxs) + COLS - 1) // COLS
    img = np.zeros((rows * CELL, COLS * CELL), np.uint8)
    for k, i in enumerate(idxs):
        r, c = divmod(k, COLS)
        g = render(i)
        img[r * CELL:r * CELL + g.shape[0], c * CELL:c * CELL + g.shape[1]] = g
    p = os.path.join(OUT, name)
    Image.fromarray(img).save(p)
    print("  保存", p, img.shape)
    return p


# 1) ASCII 自检区
save_range("00_ASCII自检_idx0-93.png", list(range(0, 94)))

# 2) 重点核对：已实测坏字位的邻近区
FOCUS = list(range(230, 250))       # 三(239) 附近
FOCUS += list(range(340, 355))      # 伙347/会348 附近
FOCUS += list(range(1020, 1080))    # 延1025..弗1034 附近
FOCUS += list(range(1050, 1070))
FOCUS += list(range(1890, 1920))    # 社1908 附近
FOCUS += list(range(2090, 2110))    # 联2100 附近
FOCUS += sorted(set(FOCUS))
save_range("01_坏字位邻近区.png", FOCUS)

# 3) 全字表分段
SEG = 300
nseg = (N + SEG - 1) // SEG
for s in range(nseg):
    idxs = list(range(s * SEG, min(N, (s + 1) * SEG)))
    save_range("10_全表_%02d_idx%d-%d.png" % (s, idxs[0], idxs[-1]), idxs)
print("\n完成，输出目录", OUT)