# -*- coding: utf-8 -*-
"""从截图提取字形位图"""
from PIL import Image
import numpy as np, os

S1 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg'
S2 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T08-17-55-901Z-fad3050f.jpg'
OUT = r'F:\sr2-cn\_glyphs'
os.makedirs(OUT, exist_ok=True)

def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(np.float32)

def find_rows(a, y0, y1, thr=170, minc=20):
    g = a[y0:y1].max(axis=2)
    prof = (g > thr).sum(axis=1)
    rows = [i + y0 for i, v in enumerate(prof) if v >= minc]
    return rows, prof

a1 = load(S1)
a2 = load(S2)

print("S1 字幕行搜索 (600..780):")
rows, prof = find_rows(a1, 600, 780)
if rows:
    print("   rows %d..%d" % (rows[0], rows[-1]))
    # 打印 profile 峰值
    top = sorted(range(len(prof)), key=lambda i: -prof[i])[:8]
    print("   峰值 y:", [(i + 600, prof[i]) for i in top])

print("S2 HUD 行搜索 (40..160):")
rows2, prof2 = find_rows(a2, 40, 170)
if rows2:
    print("   rows %d..%d" % (rows2[0], rows2[-1]))
    top = sorted(range(len(prof2)), key=lambda i: -prof2[i])[:10]
    print("   峰值 y:", [(i + 40, prof2[i]) for i in top])

# 列分割
def cols(a, y0, y1, thr=170, gap=3):
    g = a[y0:y1].max(axis=2)
    cp = (g > thr).sum(axis=0)
    segs = []
    cur = None
    for x, v in enumerate(cp):
        if v > 0:
            if cur is None:
                cur = [x, x]
            else:
                cur[1] = x
        else:
            if cur is not None:
                if x - cur[1] > gap:
                    segs.append(tuple(cur)); cur = None
    if cur: segs.append(tuple(cur))
    return segs, cp
