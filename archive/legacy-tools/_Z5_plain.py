# -*- coding: utf-8 -*-
import sys, struct, io, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

A = Vpp(r"F:\sr2-cn\_patchsrc\patch.vpp_pc")
B = Vpp(r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc")
ca = parse_plain(A.read(A.find("charlist_CH", "txt")))
cb = parse_plain(B.read(B.find("charlist_CH", "txt")))
print("AUTHOR count=%d  GAME count=%d  identical=%s" % (len(ca), len(cb), ca == cb))
if ca != cb:
    for i in range(min(len(ca), len(cb))):
        if ca[i] != cb[i]:
            print("  first diff at %d: author U+%04X game U+%04X" % (i, ca[i], cb[i]))
            break
    print("  author extra tail:", ca[len(cb):][:20])
    print("  game extra tail:", cb[len(ca):][:20])
print("author 你 index:", ca.index(0x4F60) if 0x4F60 in ca else None)
print("game   你 index:", cb.index(0x4F60) if 0x4F60 in cb else None)
print("author 任 index:", ca.index(0x4EFB) if 0x4EFB in ca else None)
print()
# scan DLC / patches dirs for vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
for sub in ('DLC', 'patches', 'Mods'):
    p = os.path.join(G, sub)
    if os.path.isdir(p):
        for dp, dn, fn in os.walk(p):
            for f in fn:
                if f.lower().endswith(('.vpp_pc', '.le_strings', '.txt')):
                    print(os.path.join(dp, f), os.path.getsize(os.path.join(dp, f)))
