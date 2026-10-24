# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp
from _img import dxt3_decode

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
at = pv.read(pv.find("fnt_chinese", "g_peg_pc"))
px = dxt3_decode(at, 2048, 2048)
W = H = 2048

def block(x, y, n=16):
    """n x n mean-normalised alpha mask (upscale from 30x30)"""
    g = [0]*(n*n)
    for j in range(n):
        for i in range(n):
            # sample centre of corresponding 28/n area
            sx = x + i*30//n
            sy = y + j*30//n
            o = (sy*W+sx)*4
            g[j*n+i] = px[o+3]
    return g

def score(a, b):
    return sum(abs(a[i]-b[i]) for i in range(len(a)))

tpl_ren = block(1+31*11, 1+31*5)     # 任 at idx336
tpl_zhi = block(1+31*(403%65), 1+31*(403//65))  # 值 at idx403

N = 16
P = 65
rows = H // 31 + 1
cols = W // 31 + 1
hits_r, hits_z = [], []
for r in range(rows):
    y = 1 + 31*r
    if y + 30 > H: break
    for c in range(cols):
        x = 1 + 31*c
        if x + 30 > W: break
        g = block(x, y)
        if score(g, tpl_ren) < 3000:
            hits_r.append((r, c, x, y, score(g, tpl_ren)))
        if score(g, tpl_zhi) < 3000:
            hits_z.append((r, c, x, y, score(g, tpl_zhi)))
print("grid rows max", rows, "cols max", cols)
print("任 matches:", len(hits_r))
for h in hits_r[:12]:
    r, c, x, y, s = h
    print("   row=%d col=%d idx65=%d" % (r, c, r*65+c))
print("值 matches:", len(hits_z))
for h in hits_z[:12]:
    r, c, x, y, s = h
    print("   row=%d col=%d" % (r, c))
