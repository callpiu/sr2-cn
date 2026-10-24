# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode, crop_png

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
at = pv.read(pv.find("fnt_chinese", "g_peg_pc"))
px = dxt3_decode(at, 2048, 2048)
P = 65
for i in (1887, 1855, 336, 403):
    x, y = 1 + 31 * (i % P), 1 + 31 * (i // P)
    crop_png(px, 2048, 2048, x, y, 30, 30, 6, r'F:\sr2-cn\_AT_%04d.png' % i)
    print(i, (x, y))
