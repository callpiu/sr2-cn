# -*- coding: utf-8 -*-
import sys, struct, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
found = []
for vf in ('common.vpp_pc', 'patch.vpp_pc', 'textures.vpp_pc', 'pegs.vpp_pc'):
    p = os.path.join(G, vf)
    if not os.path.exists(p):
        continue
    v = Vpp(p)
    for e in v.entries():
        if e['name'] in ('fnt_body_n', 'fnt_body_s') and e['ext'] in ('vf3_pc', 'g_peg_pc'):
            found.append((vf, e['name'], e['ext'], e['size'], v.read(e)))
for vf, nm, ext, sz, d in found:
    if ext != 'vf3_pc':
        print(vf, nm, ext, sz)
        continue
    N = struct.unpack_from('<I', d, 8)[0]
    u_at, v_at = 0xBC + N*16, 0xBC + N*16 + N*4
    print("%s %s %s size=%d N=%d header_end=%d 0xB0-0x110=%s" %
          (vf, nm, ext, sz, N, v_at + N*4, d[0xB0:0x110].hex(' ')))
    # atlas name string search
    import re
    ms = re.findall(rb'[ -~]{6,40}\.peg', d)
    print("   name strings:", ms[:6])
