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

JP = [467, 1869, 276, 1705, 1627, 340, 919, 1648, 303, 287, 301, 270, 336]
CELL = 34
canvas = bytearray(CELL*CELL*4*len(JP))
for k, i in enumerate(JP):
    x, y = U[i], V[i]
    for j in range(CELL):
        for ii in range(CELL):
            sx, sy = x + ii*30//CELL, y + j*30//CELL
            o = (sy*2048 + sx)*4
            q = (j*CELL*len(JP) + (k*CELL + ii))*4
            canvas[q:q+4] = px[o:o+4]
write_png(r'F:\sr2-cn\_JProw.png', canvas, CELL*len(JP), CELL)
print("static_JP slots rendered:", JP)
print("expect img line1: 任璨偶巧位校衡勾远藐乱携")
