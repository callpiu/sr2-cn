# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode, crop_png

OFFC = Vpp(r"F:\sr2-cn\_backup_F\common.official_20261013_175139.vpp_pc")
vf = OFFC.read(OFFC.find("fnt_chinese", "vf3_pc"))
print("official vf3 size", len(vf), "head", vf[:16].hex(' '))
N = struct.unpack_from('<I', vf, 8)[0]
print("N =", N)
u_at = 0xBC + N*16
v_at = u_at + N*4
print("u_at=0x%X v_at=0x%X end=0x%X filelen=0x%X" % (u_at, v_at, v_at+N*4, len(vf)))
U = struct.unpack_from('<%dI' % N, vf, u_at)
V = struct.unpack_from('<%dI' % N, vf, v_at)
for s in (403, 1868, 1067, 454, 364, 2699, 2328, 423, 1222):
    print("  slot %4d -> UV(%4d,%4d)" % (s, U[s], V[s]))
# where is the 任 glyph (342,156) in official vf3?
for i in range(N):
    if (U[i], V[i]) == (342, 156):
        print("  glyph at (342,156) is official vf3 index", i)
        break
# decode NEW atlas at those UVs
NEW = Vpp(r"G:\SteamLibrary\steamapps\common\Saints Row 2\textures.vpp_pc")
an = None
for e in NEW.entries():
    if e['name'] == 'fnt_chinese' and e['size'] == 4194304:
        an = NEW.read(e)
px = dxt3_decode(an, 2048, 2048)
for s in (403, 1868, 1067, 454, 364, 2699, 2328, 423, 1222):
    crop_png(px, 2048, 2048, U[s], V[s], 30, 30, 6, r'F:\sr2-cn\_OV_%04d.png' % s)
print("crops written")
