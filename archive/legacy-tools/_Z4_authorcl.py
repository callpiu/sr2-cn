# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse(d):
    m = re.search(rb'count=(\d+)\r?\n', d)
    return m, [int(x) for x in re.findall(rb'\d+', d[m.end():])] if m else (None, [])

A = Vpp(r"F:\sr2-cn\_patchsrc\patch.vpp_pc")
B = Vpp(r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc")
da = A.read(A.find("charlist_CH", "txt"))
db = B.read(B.find("charlist_CH", "txt"))
ma, ca = parse(da)
mb, cb = parse(db)
print("AUTHOR charlist: count=%s parsed=%d size=%d" % (ma.group(1).decode(), len(ca), len(da)))
print("GAME   charlist: count=%s parsed=%d size=%d" % (mb.group(1).decode(), len(cb), len(db)))
print("author head:", da[:300])
print()
for name, cl in (('AUTHOR', ca), ('GAME', cb)):
    print("--- %s ---" % name)
    for i in (336, 371, 403, 364, 423, 454, 1067, 1222, 1868, 2328, 2699):
        if i < len(cl):
            print("   cl[%4d] = U+%04X %s" % (i, cl[i], chr(cl[i])))
