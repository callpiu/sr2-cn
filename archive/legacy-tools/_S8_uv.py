# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
vf = pv.read(pv.find("fnt_chinese", "vf3_pc"))
print("vf3 len", len(vf), "head", vf[:16].hex(' '))
N = struct.unpack_from('<I', vf, 8)[0]
print("N =", N)
# header up to 0xBC
print("0x04..0x10:", vf[4:16].hex(' '))
print("0x10..0x30:", vf[16:48].hex(' '))
print("0x30..0x50:", vf[48:80].hex(' '))
print("0xB0..0xC0:", vf[0xB0:0xC0].hex(' '))
recs_at = 0xBC
# after N*16 records -> U array, V array
u_at = recs_at + N * 16
v_at = u_at + N * 4
print("recs_at", hex(recs_at), "u_at", hex(u_at), "v_at", hex(v_at), "end", hex(v_at + N*4), "filelen", hex(len(vf)))
Us = struct.unpack_from('<%dI' % N, vf, u_at)
Vs = struct.unpack_from('<%dI' % N, vf, v_at)
for i in (0, 1, 32, 93, 94, 95, 100, 200, 336, 371, 403, 511, 582, 1067, 1222, 1855, 1887):
    if i < N:
        r = struct.unpack_from('<IIII', vf, recs_at + i*16)
        print("i=%4d U=%5d V=%5d rec=%s" % (i, Us[i], Vs[i], r))
