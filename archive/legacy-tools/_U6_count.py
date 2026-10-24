# -*- coding: utf-8 -*-
import sys, struct, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
raw = pv.read(pv.find("static_CH"))
PAT = bytes.fromhex('f284ed87')
cnt = 0
st = 0
locs = []
while True:
    i = raw.find(PAT, st)
    if i < 0:
        break
    locs.append(i); cnt += 1; st = i + 1
print("occurrences:", cnt)
for i in locs:
    o = i + 4
    sl = []
    while True:
        v = struct.unpack_from('>H', raw, o)[0]; o += 2
        if v == 0:
            break
        sl.append(v)
        if len(sl) > 60:
            break
    print("  at %d -> %s" % (i, sl))
