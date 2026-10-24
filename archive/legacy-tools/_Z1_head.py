# -*- coding: utf-8 -*-
import sys, struct, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
cv = Vpp(G + r"\common.vpp_pc")
for nm in ('fnt_chinese', 'fnt_body_n'):
    d = cv.read(cv.find(nm, 'vf3_pc'))
    print("=== %s  size=%d ===" % (nm, len(d)))
    for base in range(0, 0xC0, 16):
        row = d[base:base+16]
        u32 = struct.unpack_from('<4I', row, 0) if len(row) == 16 else ()
        print("  0x%02X: %s   %s" % (base, row.hex(' '), u32))
    # records at 0xBC
    print("  rec[0..3]:", [struct.unpack_from('<IIII', d, 0xBC+i*16) for i in range(4)])
