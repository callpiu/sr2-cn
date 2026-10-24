# -*- coding: utf-8 -*-
"""提取字幕字形 + 图集全搜索模板匹配"""
from PIL import Image, ImageFilter
import numpy as np, os, struct

S1 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg'
OUT = r'F:\sr2-cn\_glyphs'
os.makedirs(OUT, exist_ok=True)

# ---------- 1. 字幕区域 ----------
im = Image.open(S1).convert('RGB')
y0, y1 = 696, 740
band = im.crop((700, y0, 1350, y1))
g = np.asarray(band.convert('L')).astype(np.float32)
# 高通: 减去背景
bg = np.asarray(band.convert('L').filter(ImageFilter.BoxBlur(7))).astype(np.float32)
ink = np.clip(g - bg + 40, 0, 255)
print("band", band.size, "ink max", ink.max())

# 列投影找字形
cp = (ink > 70).sum(axis=0)
segs = []
cur = None
for x, v in enumerate(cp):
    if v > 0:
        cur = [x, x] if cur is None else [cur[0], x]
    else:
        if cur is not None and x - cur[1] >= 3:
            segs.append(tuple(cur)); cur = None
if cur: segs.append(tuple(cur))
segs = [s for s in segs if s[1] - s[0] >= 6]
print("字形列段 %d 个:" % len(segs), segs)

# ---------- 2. 逐个导出字形 ----------
glyphs = []
for i, (a, b) in enumerate(segs):
    sub = ink[:, a:b + 1]
    rp = (sub > 70).sum(axis=1)
    ys = [y for y, v in enumerate(rp) if v > 0]
    if not ys:
        continue
    t, bb = ys[0], ys[-1]
    patch = sub[t:bb + 1]
    glyphs.append(dict(x0=a, x1=b, y0=t, y1=bb, w=b - a + 1, h=bb - t + 1, patch=patch))
    Image.fromarray(patch.astype(np.uint8)).save(os.path.join(OUT, 'sub_%02d.png' % i))
print("导出字形:", [(gl['w'], gl['h']) for gl in glyphs])

np.save(os.path.join(OUT, 'ink.npy'), ink)
import pickle
pickle.dump(glyphs, open(os.path.join(OUT, 'glyphs.pkl'), 'wb'))
