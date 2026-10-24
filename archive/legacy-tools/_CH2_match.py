# -*- coding: utf-8 -*-
"""按 31.4px 步距切分字幕字形，并在图集中全搜索匹配"""
from PIL import Image, ImageFilter
import numpy as np, os, struct

S1 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg'
OUT = r'F:\sr2-cn\_glyphs'
os.makedirs(OUT, exist_ok=True)

# 图集
AT = np.frombuffer(open(r'F:\sr2-cn\_fontdump\fnt_chinese.tex', 'rb').read(), dtype=np.uint8)
AT = AT.reshape(2048, 2048).astype(np.float32)

# vf3 的 P 值 (x 坐标候选)
d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
B = 0xBC + N * 16
P = [struct.unpack_from('<I', d, B + i * 8)[0] for i in range(N)]
Pset = sorted(set(P))
print("P 候选 x:", len(Pset), Pset[:8], Pset[-4:])

# 截图字幕
im = Image.open(S1).convert('L')
g = np.asarray(im).astype(np.float32)
bg = np.asarray(im.filter(ImageFilter.BoxBlur(7))).astype(np.float32)
ink = np.clip(g - bg, 0, 255)
print("ink shape", ink.shape)

# 定位字幕行
band = ink[696:740, 700:1350]
cp = (band > 55).sum(axis=0)
xs = [x for x, v in enumerate(cp) if v > 0]
x0, x1 = xs[0] + 700, xs[-1] + 700
print("字幕 x 范围 %d..%d 宽 %d" % (x0, x1, x1 - x0 + 1))
NC = 11
pitch = (x1 - x0 + 1) / NC
print("pitch = %.2f" % pitch)

rp = (ink[690:745, x0:x1 + 1] > 55).sum(axis=1)
ys = [y for y, v in enumerate(rp) if v > 0]
ty, by = ys[0] + 690, ys[-1] + 690
print("字幕 y 范围 %d..%d 高 %d" % (ty, by, by - ty + 1))

def ssd_best(tmpl):
    th, tw = tmpl.shape
    t = tmpl - tmpl.mean()
    tn = np.sqrt((t * t).sum())
    best = []
    for cx in Pset:
        if cx + tw > 2048:
            continue
        col = AT[0:1400, cx:cx + tw]           # (1400, tw)
        # 滑动窗口均值与能量
        csum = np.cumsum(np.cumsum(col, axis=0), axis=1)
        csum2 = np.cumsum(np.cumsum(col * col, axis=0), axis=1)
        def rect(c, y):
            return c[y + th - 1, tw - 1]
        # 简易: 逐 y 计算
        for y in range(0, 1400 - th):
            w = col[y:y + th]
            wm = w.mean()
            num = ((w - wm) * t).sum()
            den = np.sqrt(((w - wm) ** 2).sum()) * tn + 1e-6
            score = num / den
            best.append((score, cx, y))
    best.sort(reverse=True)
    return best[:6]

results = []
for i in range(NC):
    a = int(round(x0 + i * pitch))
    b = int(round(x0 + (i + 1) * pitch))
    tmpl = ink[ty:by + 1, a:b]
    Image.fromarray(tmpl.astype(np.uint8)).save(os.path.join(OUT, 'c_%02d.png' % i))
    res = ssd_best(tmpl)
    results.append((i, a, b, res))
    print("\n#%d x=%d..%d  top:" % (i, a, b))
    for s, cx, y in res:
        print("      score=%.3f  x=%d y=%d" % (s, cx, y))
