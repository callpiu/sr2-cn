import numpy as np, os
from PIL import Image

RAW = r"F:\sr2-cn\_fontdump\fnt_chinese.tex"
W = H = 2048
a = np.fromfile(RAW, dtype=np.uint8).reshape(H, W)
ink = (a > 110)

rs = ink.sum(axis=1)
cs = ink.sum(axis=0)

def bands(v, thr=1):
    out = []
    s = None
    for i, x in enumerate(v):
        if x > thr and s is None:
            s = i
        elif x <= thr and s is not None:
            out.append((s, i - 1)); s = None
    if s is not None:
        out.append((s, len(v) - 1))
    return out

rb = bands(rs)
cb = bands(cs)
print("行带数 =", len(rb))
print("行带前 12:", rb[:12])
print("行带后 6 :", rb[-6:])
print("行起始 pitch:", [rb[i+1][0]-rb[i][0] for i in range(min(10, len(rb)-1))])
print("列带数 =", len(cb))
print("列带前 8:", cb[:8])
print("列起始 pitch:", [cb[i+1][0]-cb[i][0] for i in range(min(10, len(cb)-1))])

# 行带起点序列(取内容行)
rows = [b[0] for b in rb]
cols = [b[0] for b in cb]
print("rows n=%d  first=%s last=%s" % (len(rows), rows[:5], rows[-5:]))
print("cols n=%d  first=%s last=%s" % (len(cols), cols[:5], cols[-5:]))
