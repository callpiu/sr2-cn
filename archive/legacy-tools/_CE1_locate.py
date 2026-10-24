# -*- coding: utf-8 -*-
"""定位截图中字幕文字行并切分字形"""
from PIL import Image
import numpy as np

S1 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg'
im = Image.open(S1).convert('RGB')
a = np.asarray(im).astype(np.int16)
print("image", a.shape)

# 亮度 + 低饱和度 => 文字（白色/灰色/绿色文字）
mx = a.max(axis=2); mn = a.min(axis=2)
bright = (mx > 150) & ((mx - mn) < 120)
prof = bright.sum(axis=1)
for y in range(600, 780, 5):
    print("  y=%d count=%d" % (y, prof[y]))
