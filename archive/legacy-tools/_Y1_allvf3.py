# -*- coding: utf-8 -*-
import sys, struct, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
# collect every *.vf3_pc in common/patch and check U[403],V[403] etc.
SLOTS = [403, 1868, 1067, 454, 364, 2699, 2328, 423, 1222]
TARGET_UV = {403:(342,156), 1868:(900,838), 1067:(621,187), 454:(1768,435),
             364:(1148,156), 2699:(1737,1241), 2328:(1799,1055), 423:(900,156),
             1222:(63,1117)}

for vfn in ('common.vpp_pc', 'patch.vpp_pc'):
    v = Vpp(os.path.join(G, vfn))
    for e in v.entries():
        if e['ext'] != 'vf3_pc':
            continue
        d = v.read(e)
        if d[:4] != b'VFNT' or len(d) < 0x100:
            continue
        N = struct.unpack_from('<I', d, 8)[0]
        if N < 500:
            continue
        u_at = 0xBC + N*16
        v_at = u_at + N*4
        if v_at + N*4 > len(d):
            print("%-16s %-14s N=%d  (truncated)" % (vfn, e['name'], N))
            continue
        U = struct.unpack_from('<%dI' % N, d, u_at)
        V = struct.unpack_from('<%dI' % N, d, v_at)
        ms = re.findall(rb'[ -~]{5,40}\.peg', d)
        hit = 0
        for s in SLOTS:
            if s < N and (U[s], V[s]) == TARGET_UV[s]:
                hit += 1
        print("%-16s %-14s N=%-5d peg=%-20s matches=%d/9  UV[403]=%s" %
              (vfn, e['name'], N, ms[0].decode() if ms else '?', hit,
               (U[403], V[403]) if 403 < N else 'OOR'))
