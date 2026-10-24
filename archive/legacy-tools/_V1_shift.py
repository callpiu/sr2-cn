# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode, crop_png

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
vf = pv.read(pv.find("fnt_chinese", "vf3_pc"))
at = pv.read(pv.find("fnt_chinese", "g_peg_pc"))
px = dxt3_decode(at, 2048, 2048)
N = struct.unpack_from('<I', vf, 8)[0]
print("vf3 N =", N, " field@0x0C =", struct.unpack_from('<I', vf, 12)[0])
U = struct.unpack_from('<%dI' % N, vf, 0xBC + N*16)
V = struct.unpack_from('<%dI' % N, vf, 0xBC + N*16 + N*4)
# where does 任(U+4EFB, target glyph at uv 342,156) live in the U/V array?
target = (342, 156)
for i in range(N):
    if (U[i], V[i]) == target:
        print("任 glyph is at vf3 index", i)
        break
for i in range(N):
    if (U[i], V[i]) == (404, 187):
        print("值 glyph at vf3 index", i)
        break
# crop a few neighbours of 403 to inspect
for i in (336, 368, 371, 403, 435, 439):
    x, y = U[i], V[i]
    crop_png(px, 2048, 2048, x, y, 30, 30, 6, r'F:\sr2-cn\_SH_%04d.png' % i)
    print("vf3[%d] UV=(%d,%d)" % (i, x, y))
