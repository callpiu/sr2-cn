# -*- coding: utf-8 -*-
import sys, struct, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
for vf in ('common.vpp_pc', 'patch.vpp_pc', 'textures.vpp_pc', 'pegs.vpp_pc',
           'anims.vpp_pc', 'audio.vpp_pc', 'meshes.vpp_pc'):
    p = os.path.join(G, vf)
    if not os.path.exists(p):
        continue
    v = Vpp(p)
    for e in v.entries():
        nm = (e['name'] + '.' + e['ext']).lower()
        if 'charlist' in nm:
            d = v.read(e)
            print("%-16s %4d %-22s size=%-7d head=%s" %
                  (vf, e['idx'], nm, e['size'], d[:60]))
