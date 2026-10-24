# -*- coding: utf-8 -*-
"""用列投影自相关求图集水平/垂直周期"""
raw = open(r'F:\sr2-cn\_fontdump\fnt_chinese.tex', 'rb').read()
W = H = 2048
colsum = [0] * W
rowsum = [0] * H
for y in range(H):
    line = raw[y*W:(y+1)*W]
    for x in range(W):
        if line[x]:
            colsum[x] += 1
            rowsum[y] += 1

print("colsum[0:130]:", colsum[:130])
print("rowsum[0:130]:", rowsum[:130])

def best_period(sig, lo=20, hi=80):
    res = []
    for p in range(lo, hi+1):
        s = 0
        for i in range(0, len(sig) - p):
            s += sig[i] * sig[i+p]
        res.append((s, p))
    res.sort(reverse=True)
    return res[:8]

print("\ncolsum 最佳周期:", best_period(colsum))
print("rowsum 最佳周期:", best_period(rowsum))
