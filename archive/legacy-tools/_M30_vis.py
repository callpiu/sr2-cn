# -*- coding: utf-8 -*-
# 视觉验证：第357格（应为 们）vs 第327格（们的原格）
import sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, png_gray

OUT = r"F:/sr2-cn/_FIX/patch_weifix.vpp_pc"
SRC = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
f = Font(OUT)
fo = Font(SRC)
CELL, PAD, SZ = 31, 4, 31 + 8
SC = 8
GAP = 6
COLS = 4


def cell(A, k):
    from sr2font import dec_block
    x, y = f.uv(k)
    x -= PAD
    y -= PAD
    return [[dec_block(A, (((y + yy) // 4) * 512 + ((x + xx) // 4)) * 16)[(y + yy) % 4][(x + xx) % 4][3]
             for xx in range(SZ)] for yy in range(SZ)]


items = [
    ("新357格(应为们)", cell(f.atlas, 357)),
    ("327格(们的原格)", cell(f.atlas, 327)),
    ("旧357格(原为位)", cell(fo.atlas, 357)),
    ("旧327格(原为们)", cell(fo.atlas, 327)),
]
w = COLS * (SZ * SC + GAP)
h = ((len(items) + COLS - 1) // COLS) * (SZ * SC + GAP)
cv = [[20] * w for _ in range(h)]
for n, (lab, g) in enumerate(items):
    ox = (n % COLS) * (SZ * SC + GAP)
    oy = (n // COLS) * (SZ * SC + GAP)
    for yy in range(SZ):
        for xx in range(SZ):
            v = g[yy][xx]
            for dy in range(SC):
                for dx in range(SC):
                    cv[oy + yy * SC + dy][ox + xx * SC + dx] = v
png_gray(cv, 1, r"F:/sr2-cn/_verify_357.png")
print("输出 F:/sr2-cn/_verify_357.png")
print("顺序: 新357 | 327 | 旧357 | 旧327")
print("UV: 357 ->", f.uv(357), "  327 ->", f.uv(327))
