# -*- coding: utf-8 -*-
"""Decisive: decode fnt_chinese atlas, crop glyphs at index 403/371/336/1887/1855."""
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode, crop_png

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
at = pv.read(pv.find("fnt_chinese", "g_peg_pc"))
W = H = 2048
px = dxt3_decode(at, W, H)
print("decoded", len(px))

P = 65
def uv(i):
    return (1 + 31 * (i % P), 1 + 31 * (i // P))

CASES = [(403, '应显示你(乱码任)'), (371, 'cl索引=你'), (336, 'cl索引=任'),
         (1887, 'HUD直(正常)'), (1855, 'cl索引=直')]
for i, note in CASES:
    x, y = uv(i)
    p = r'F:\sr2-cn\_GLY_%04d.png' % i
    crop_png(px, W, H, x, y, 30, 30, 6, p)
    print(i, note, "uv=", (x, y), "->", p)
