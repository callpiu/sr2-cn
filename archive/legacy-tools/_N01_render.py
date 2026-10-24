# -*- coding: utf-8 -*-
# 贴图遮盖 第1步：用图集中的「正确字形」拼接出两句字幕的正确文本图片
# 每个字从 charlist 正确格取（格号 = B.index(字)，图集第k格 = charlist[k+5]，
# 所以正确字形的实际存储格 = B.index(字) - 5）
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, dec_block, enc_block, png_gray

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
OFF = 5
CELL, PAD, SZ = 31, 3, 31 + 6

TEXTS = [
    ("sub1", "你的弟兄们需要你的保护"),
    ("sub2", "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"),
]

def cell_gray(k):
    """取图集第 k 格的字形（灰度，SZ×SZ）"""
    x, y = f.uv(k)
    x -= PAD
    y -= PAD
    return [[dec_block(f.atlas, (((y + yy) // 4) * 512 + ((x + xx) // 4)) * 16)[(y + yy) % 4][(x + xx) % 4][3]
             for xx in range(SZ)] for yy in range(SZ)]

# 渲染：黑底白字，字间距 2 像素
GAP = 2
for tag, text in TEXTS:
    W = len(text) * (SZ + GAP) + GAP
    H = SZ + 8
    img = [[0] * W for _ in range(H)]
    for i, ch in enumerate(text):
        if ch not in bidx:
            print("  !! 字不在 charlist: %s" % ch); continue
        k = bidx[ch] - OFF          # 正确字形的存储格
        g = cell_gray(k)
        ox = GAP + i * (SZ + GAP)
        oy = 4
        for yy in range(SZ):
            for xx in range(SZ):
                img[oy + yy][ox + xx] = g[yy][xx]
    png_gray(img, 1, r"F:/sr2-cn/_ovl_%s.png" % tag)
    print("%s: %d 字 -> %dx%d  已存 _ovl_%s.png" % (tag, len(text), W, H, tag))
