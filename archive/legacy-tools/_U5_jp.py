# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")

def parse(d):
    m = re.search(rb'count=(\d+)\r?\n', d)
    if not m:
        return []
    return [int(x) for x in re.findall(rb'\d+', d[m.end():])]

EXP = {403: 0x4EFB, 364: 0x4F4D, 423: 0x4F2A, 454: 0x5DE7, 1067: 0x5076,
       1222: 0x8BE5, 1868: 0x74A8, 2328: 0x8861, 2699: 0x96C4}

for nm in ('jpcharlist', 'charlist_jp', 'charlist_ch'):
    e = pv.find(nm, 'txt')
    if not e:
        print(nm, "not found"); continue
    t = parse(pv.read(e))
    print("%-12s count=%d" % (nm, len(t)))
    ok = 0
    for slot, cp in EXP.items():
        got = t[slot] if slot < len(t) else None
        mark = 'OK' if got == cp else ''
        if mark: ok += 1
        print("    slot=%4d expect U+%04X got %s %s" %
              (slot, cp, ('U+%04X' % got) if got else 'OOR', mark))
    print("    matched %d/9" % ok)
