# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode, crop_png

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
rawcl = pv.read(pv.find("charlist_CH", "txt"))
if rawcl is None or len(rawcl) < 100:
    cands = [e for e in pv.entries() if 'charlist' in (e['name']+e['ext']).lower()]
    for e in cands:
        print("cand", e['idx'], e['name'], e['ext'], e['size'])
    rawcl = pv.read(cands[0])
print("charlist size", len(rawcl))
m = re.search(rb'count=(\d+)\r?\n', rawcl)
cl = [int(x) for x in re.findall(rb'\d+', rawcl[m.end():])]
print("count field", m.group(1), "parsed", len(cl))
for i in (336, 371, 403, 364, 423, 454, 1067, 1222, 1868, 2328, 2699):
    if i < len(cl):
        print("cl[%4d] = U+%04X %s" % (i, cl[i], chr(cl[i]) if 0x20 < cl[i] < 0x3000 else ''))
