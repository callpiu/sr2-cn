# -*- coding: utf-8 -*-
"""带 idx 标签的放大渲染，用于逐字核对错位。"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
import numpy as np
from PIL import Image, ImageDraw
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

OUT = r"F:/sr2-cn/_字体核对"
os.makedirs(OUT, exist_ok=True)
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
vf3 = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
U = list(struct.unpack_from("<%di" % N, vf3, 0xAF6C))
V = list(struct.unpack_from("<%di" % N, vf3, 0xDB18))
_, alpha = sr2lib.dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))),
                               2048, 2048)

CELL, SCALE, COLS = 31, 3, 20
LBL = 14          # 标签行高(放大后)


def glyph(i):
    x, y = U[i], V[i]
    g = alpha[y:y + 28, x:x + CELL]
    out = np.zeros((28, CELL), np.uint8)
    h, w = min(28, g.shape[0]), min(CELL, g.shape[1])
    out[:h, :w] = g[:h, :w]
    return out


def sheet(name, idxs, scale=SCALE, cols=COLS):
    cw, chh = CELL * scale, 28 * scale + LBL
    rows = (len(idxs) + cols - 1) // cols
    img = Image.new("L", (cols * cw, rows * chh), 0)
    d = ImageDraw.Draw(img)
    for k, i in enumerate(idxs):
        r, c = divmod(k, cols)
        px = c * cw
        py = r * chh
        g = glyph(i)
        im = Image.fromarray(g).resize((CELL * scale, 28 * scale), Image.NEAREST)
        img.paste(im, (px, py + LBL))
        ch = chr(CPS[i]) if 0 <= CPS[i] < 0x10000 else "?"
        d.text((px + 2, py + 1), "%d:%s" % (i, ch), fill=200)
    p = os.path.join(OUT, name)
    img.save(p)
    print("  ", p, img.size)
    return p


print("=== 坏字位邻近区（带标签）===")
# 三=239/丈=238；伙=347/会=348；延1025..弗1034；社1908；联2100
sheet("20_三伙会区_idx225-260.png", list(range(225, 261)))
sheet("21_伙会区_idx335-365.png", list(range(335, 366)))
sheet("22_idx-32坏区_idx1015-1075.png", list(range(1015, 1076)))
sheet("23_社附近_idx1895-1925.png", list(range(1895, 1926)))
sheet("24_联附近_idx2085-2115.png", list(range(2085, 2116)))