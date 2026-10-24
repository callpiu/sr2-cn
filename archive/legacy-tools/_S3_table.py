# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
raw = pv.read(pv.find("static_CH"))
buck = 1024
for base, order in ((0x0C, 'count_first'), (0x10, 'off_first')):
    tot = 0
    ok = True
    firsts = []
    for i in range(buck):
        a = struct.unpack_from('<I', raw, base + i*8)[0]
        b = struct.unpack_from('<I', raw, base + i*8 + 4)[0]
        if order == 'count_first':
            cnt, off = a, b
        else:
            off, cnt = a, b
        tot += cnt
        if i < 3:
            firsts.append((off, cnt))
        if off < base + buck*8 or off >= len(raw):
            ok = False
    print(order, "sum(count)=", tot, "all offsets in range:", ok, "first:", firsts)
