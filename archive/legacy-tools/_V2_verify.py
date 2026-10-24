# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode, write_png

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
vf = pv.read(pv.find("fnt_chinese", "vf3_pc"))
at = pv.read(pv.find("fnt_chinese", "g_peg_pc"))
px = dxt3_decode(at, 2048, 2048)
N = struct.unpack_from('<I', vf, 8)[0]
U = struct.unpack_from('<%dI' % N, vf, 0xBC + N*16)
V = struct.unpack_from('<%dI' % N, vf, 0xBC + N*16 + N*4)

IDX = [336, 1784, 410, 967, 362, 2656, 2268, 354, 2342, 403, 1868, 1067]
CELL = 34
canvas = bytearray(CELL*CELL*4*len(IDX))
for k, i in enumerate(IDX):
    x, y = U[i], V[i]
    for j in range(CELL):
        for ii in range(CELL):
            sx, sy = x + ii*30//CELL, y + j*30//CELL
            o = (sy*2048 + sx)*4
            q = ((j)*CELL*len(IDX) + (k*CELL + ii))*4
            canvas[q:q+4] = px[o:o+4]
write_png(r'F:\sr2-cn\_VERIFY_row.png', canvas, CELL*len(IDX), CELL)
print("indices:", IDX)
for k, i in enumerate(IDX):
    print("  pos %d = index %d (UV %d,%d)" % (k, i, U[i], V[i]))
