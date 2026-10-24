# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
cands = [e for e in pv.entries() if 'chinese' in (e['name'] + e['ext']).lower()]
for e in cands:
    print(e['idx'], e['name'], e['ext'], e['size'])
