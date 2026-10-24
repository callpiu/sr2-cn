# -*- coding: utf-8 -*-
"""渲染「官方 common 字体」图集（textures.vpp_pc 内 fnt_chinese）的指定字形。

用途：验证「活动 HUD 用官方字表」假设 —— 官方图集 cell i 的字形，
是否正是屏幕上乱码显示的那批错字（T[332]=位 / T[371]=任 / T[422]=巧 / T[1035]=偶 / T[1836]=璨）。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
import numpy as np
from PIL import Image, ImageDraw
import sr2lib as S

sys.stdout.reconfigure(encoding="utf-8")
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:/sr2-cn/_字体核对"
os.makedirs(OUT, exist_ok=True)

# --- 1. common vf3 的 U/V ---
vp = S.Vpp(os.path.join(G, "common.vpp_pc"))
vf3 = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
N = struct.unpack_from("<I", vf3, 8)[0]
U = list(struct.unpack_from("<%di" % N, vf3, 45596))
V = list(struct.unpack_from("<%di" % N, vf3, 45596 + N * 4))

# --- 2. 汉化 charlist（用于对照标注） ---
CPS = [int(x) for x in vp.read(vp.find("charlist_CH", "txt")).split() if x.isdigit()] if False else None
vp2 = S.Vpp(os.path.join(G, "patch.vpp_pc"))
CPS = [int(l) for l in vp2.read(vp2.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
print("common 字形数 N=%d  汉化 charlist=%d" % (N, len(CPS)))

# --- 3. 官方图集（textures.vpp_pc，只读头部+seek 单条目，绝不整体打开） ---
TEX = os.path.join(G, "textures.vpp_pc")
BODY, SIZE = 85407184, 4194304
with open(TEX, "rb") as f:
    f.seek(BODY)
    raw = f.read(SIZE)
print("读图集 %d 字节" % len(raw))
_, alpha = S.dxt3_decode(raw, 2048, 2048)
print("alpha shape", alpha.shape)

CELL_W, CELL_H = 30, 30


def glyph(i, w=CELL_W, h=CELL_H):
    x, y = U[i], V[i]
    g = alpha[y:y + h, x:x + w]
    out = np.zeros((h, w), np.uint8)
    hh, ww = min(h, g.shape[0]), min(w, g.shape[1])
    out[:hh, :ww] = g[:hh, :ww]
    return out


def sheet(name, idxs, scale=4, cols=10, labeler=None):
    cw, ch = CELL_W * scale, CELL_H * scale + 16
    rows = (len(idxs) + cols - 1) // cols
    img = Image.new("L", (cols * cw, rows * ch), 0)
    d = ImageDraw.Draw(img)
    for k, i in enumerate(idxs):
        r, c = divmod(k, cols)
        px, py = c * cw, r * ch
        im = Image.fromarray(glyph(i)).resize((CELL_W * scale, CELL_H * scale), Image.NEAREST)
        img.paste(im, (px, py + 16))
        d.text((px + 2, py + 2), labeler(i) if labeler else str(i), fill=220)
    p = os.path.join(OUT, name)
    img.save(p)
    print("  ->", p, img.size)
    return p


# 目标：验证 cell332=位 / 371=任 / 422=巧 / 1035=偶 / 1836=璨
TARGET = [(332, "位?"), (371, "任?"), (422, "巧?"), (1035, "偶?"), (1836, "璨?")]
sheet("30_官方图集_验证5点.png", [i for i, _ in TARGET], scale=6, cols=5,
      labeler=lambda i: "%d=%s" % (i, dict(TARGET).get(i, "")))
# 对照组：汉化 charlist 中这些字的真实索引（任336 偶410 巧967 位362 璨1784）
CTRL = [336, 362, 410, 967, 1784]
sheet("31_官方图集_汉化索引对照.png", CTRL, scale=6, cols=5,
      labeler=lambda i: "%d(汉化=%s)" % (i, chr(CPS[i]) if i < len(CPS) else "?"))
# 连续区，看排列顺序
sheet("32_官方图集_idx330-349.png", list(range(330, 350)), scale=4, cols=10)
sheet("33_官方图集_idx366-385.png", list(range(366, 386)), scale=4, cols=10)
