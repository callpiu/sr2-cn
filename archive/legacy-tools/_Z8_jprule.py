# -*- coding: utf-8 -*-
import sys, struct, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

Z = Vpp(r"F:\sr2-cn\_patchsrc\patch.vpp_pc")
jp = parse_plain(Z.read(Z.find("charlist_JP", "txt")))
print("charlist_JP count", len(jp))
JP_SLOTS = [467, 1869, 276, 1705, 1627, 340, 919, 1648, 303, 287, 301, 270, 336]
s = ''
for v in JP_SLOTS:
    i = v - 32
    s += chr(jp[i]) if 0 <= i < len(jp) else '?'
print("static_JP decoded (index=slot-32):", s)

# also try slot direct
s2 = ''.join(chr(jp[v]) if v < len(jp) else '?' for v in JP_SLOTS)
print("static_JP decoded (index=slot)   :", s2)

# verify US
us = parse_plain(Z.read(Z.find("charlist_CZ", "txt")))  # CZ latin table as sanity
print()
print("=== search every file named *charlist* on disk ===")
for root in (r"G:\SteamLibrary\steamapps\common\Saints Row 2", r"F:\92"):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if 'charlist' in f.lower():
                p = os.path.join(dp, f)
                print("  ", os.path.getsize(p), p)
