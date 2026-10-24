# -*- coding: utf-8 -*-
"""测量图集网格间距（纯 Python）"""
raw = open(r'F:\sr2-cn\_fontdump\fnt_chinese.tex', 'rb').read()
W = H = 2048

colsum = [0] * W
rowsum = [0] * H
for y in range(H):
    base = y * W
    line = raw[base:base + W]
    for x in range(W):
        if line[x]:
            colsum[x] += 1
            rowsum[y] += 1

nzc = [i for i, v in enumerate(colsum) if v]
nzr = [i for i, v in enumerate(rowsum) if v]
print("content cols %d..%d  rows %d..%d" % (nzc[0], nzc[-1], nzr[0], nzr[-1]))

empt_c = [i for i, v in enumerate(colsum) if v == 0]
empt_r = [i for i, v in enumerate(rowsum) if v == 0]
print("empty cols:", len(empt_c), "empty rows:", len(empt_r))

# 找周期：统计相邻空列间隔
def gaps(lst, limit=None):
    g = []
    for a, b in zip(lst, lst[1:]):
        g.append(b - a)
    return g

gc = [d for d in gaps(empt_c) if d > 1]
gr = [d for d in gaps(empt_r) if d > 1]
from collections import Counter
print("col-gap histogram (top):", Counter(gc).most_common(10))
print("row-gap histogram (top):", Counter(gr).most_common(10))

# 打印前 80 个空列
print("first 60 empty cols:", empt_c[:60])
print("first 60 empty rows:", empt_r[:60])
