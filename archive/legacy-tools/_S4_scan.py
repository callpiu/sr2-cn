# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
raw = pv.read(pv.find("static_CH"))

TARGETS = {
    'F284ED87': b'\xf2\x84\xed\x87',
    '5A5AA49A': b'\x5a\x5a\xa4\x9a',
    '1738DE48': b'\x17\x38\xde\x48',
    'FB2E8DE7': b'\xfb\x2e\x8d\xe7',
}
for name, pat in TARGETS.items():
    idxs = []
    st = 0
    while True:
        i = raw.find(pat, st)
        if i < 0:
            break
        idxs.append(i)
        st = i + 1
    print(name, "BE-pos:", idxs[:5], "ctx:", [raw[i-2:i+30].hex(' ') for i in idxs[:3]])
