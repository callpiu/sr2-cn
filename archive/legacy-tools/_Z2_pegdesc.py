# -*- coding: utf-8 -*-
import sys, struct, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(G + r"\pegs.vpp_pc")
for e in pv.entries():
    if e['ext'] != 'peg_pc':
        continue
    if 'fnt' not in e['name'].lower() and 'font' not in e['name'].lower():
        continue
    d = pv.read(e)
    print("=== %s  size=%d ===" % (e['name'], len(d)))
    for base in range(0, min(len(d), 128), 16):
        print("  0x%02X: %s" % (base, d[base:base+16].hex(' ')))
