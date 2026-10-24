# -*- coding: utf-8 -*-
import os, sys, re
import numpy as np
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
OF = r"F:/sr2-cn/pristine/patch.vpp_pc"

def cl(buf):
    m = re.search(rb'count\s*=\s*(\d+)', buf)
    seg = buf[m.end():] if m else buf
    return [int(x) for x in re.findall(rb'\d+', seg)]

vG = Vpp(os.path.join(G,"patch.vpp_pc")); vO = Vpp(OF)
LC = cl(vG.read(vG.find("charlist_CH","txt")))
LO = cl(vO.read(vO.find("charlist_CH","txt")))
_, aG = dxt3_decode(vG.read(vG.find("fnt_chinese",None)), 2048, 2048)
_, aO = dxt3_decode(vO.read(vO.find("fnt_chinese",None)), 2048, 2048)
AG = aG.astype(np.float32); AO = aO.astype(np.float32)

def cell(img, k, cols=65, step=31, x0=1, y0=1):
    x = x0+step*(k%cols); y = y0+step*(k//cols)
    return img[y:y+31, x:x+31]

def ncc(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = (np.sqrt((a*a).sum())*np.sqrt((b*b).sum()))
    return float((a*b).sum()/d) if d > 1e-6 else 0.0

# 在官方图集上按 66 列 / step31 / (1,1) 扫所有格子
OFF_COLS = 66
def find_in_official(tmpl, label):
    best = []
    for row in range(43):
        for col in range(OFF_COLS):
            x = 1+31*col; y = 1+31*row
            if y+31 > 2048 or x+31 > 2048: continue
            c = AO[y:y+31, x:x+31]
            best.append((ncc(tmpl, c), col, row))
    best.sort(reverse=True)
    print("\n[%s] 官方图集中 top5 (66列网格):" % label)
    for s, col, row in best[:5]:
        print("   corr=%.3f  col=%2d row=%2d  -> 若为官方charlist序号=%d" % (s, col, row, row*OFF_COLS+col))
    return best[0]

for label, k in (("你", LC.index(0x4F60)), ("任", LC.index(0x4EFB)),
                 ("的", LC.index(0x7684)), ("弟", LC.index(0x5F1F)),
                 ("保", LC.index(0x4FDD))):
    t = cell(AG, k)
    print("\n=== %s (汉化 charlist 序号 %d) ===" % (label, k))
    find_in_official(t, label)

# 同时: 官方 charlist 里这些字的序号
for ch in "你任的弟保兄们需要护":
    try: print("官方 charlist 中 %s 序号 = %d" % (ch, LO.index(ord(ch))))
    except ValueError: print("官方 charlist 中 %s 不存在" % ch)
