# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
NEEDLES = [b'thin_overlay', b'fnt_chinese', b'header_n_overlay', b'charlist_CH']

for f in ['patch.vpp_pc', 'common.vpp_pc']:
    p = os.path.join(GAME, f)
    v = Vpp(p)
    print("=" * 70)
    print(f, "entries:", v.num)
    for e in v.entries():
        b = v.read(e)
        hits = [n.decode() for n in NEEDLES if n in b]
        if hits:
            print("  %-40s %-10s size=%-9d hits=%s" % (e['name'], e['ext'], len(b), hits))
