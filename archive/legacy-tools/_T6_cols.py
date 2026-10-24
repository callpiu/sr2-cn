# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode, crop_png

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
at = pv.read(pv.find("fnt_chinese", "g_peg_pc"))
px = dxt3_decode(at, 2048, 2048)

# candidates for slot=403 -> expected glyph "任"
CASES = []
for P in (63, 64, 65, 66, 67):
    CASES.append(('col%d' % P, 1 + 31 * (403 % P), 1 + 31 * (403 // P)))
for tag, x, y in CASES:
    crop_png(px, 2048, 2048, x, y, 30, 30, 6, r'F:\sr2-cn\_C403_%s.png' % tag)
    print(tag, (x, y))
