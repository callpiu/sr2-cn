# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")

def parse(nm):
    d = pv.read(pv.find(nm, 'txt'))
    m = re.search(rb'count=(\d+)\r?\n', d)
    return [int(x) for x in re.findall(rb'\d+', d[m.end():])]

cl = parse('charlist_ch')
jp = parse('jpcharlist')
jp2 = parse('charlist_jp')
clidx = {cp: i for i, cp in enumerate(cl)}

# slot -> target glyph index (verified for 336; others from cl index of displayed glyph)
SAMP = [(403, 336), (1868, 1784), (1067, 410), (454, 967), (364, 362),
        (2699, 2656), (2328, 2268), (423, 354), (1222, 2342)]

print("slot -> target | jp[slot] -> clidx | jp2[slot] -> clidx")
for slot, tgt in SAMP:
    a = jp[slot] if slot < len(jp) else None
    b = jp2[slot] if slot < len(jp2) else None
    print("  %4d -> %4d | U+%04X->%s | U+%04X->%s" %
          (slot, tgt, a or 0, clidx.get(a), b or 0, clidx.get(b)))
