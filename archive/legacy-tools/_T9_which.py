# -*- coding: utf-8 -*-
import sys, struct, io, os, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
for vf in ('patch.vpp_pc', 'textures.vpp_pc', 'pegs.vpp_pc', 'common.vpp_pc'):
    p = os.path.join(G, vf)
    if not os.path.exists(p):
        continue
    v = Vpp(p)
    for e in v.entries():
        if 'chinese' in (e['name']+e['ext']).lower() or 'fnt_chinese' in e['name']:
            d = v.read(e)
            print("%-16s %3d %-12s %-9s size=%-8d md5=%s" %
                  (vf, e['idx'], e['name'], e['ext'], e['size'], hashlib.md5(d).hexdigest()[:12]))
