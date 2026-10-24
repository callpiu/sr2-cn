# -*- coding: utf-8 -*-
"""验证匹配器: 图集字形 vs 图集自身; 并测试字幕字形在多个缩放下的匹配"""
from PIL import Image, ImageFilter
import numpy as np, os, struct

AT = np.frombuffer(open(r'F:\sr2-cn\_fontdump\fnt_chinese.tex', 'rb').read(),
                   dtype=np.uint8).reshape(2048, 2048).astype(np.float32)
d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
B = 0xBC + N * 16
P = [struct.unpack_from('<I', d, B + i * 8)[0] for i in range(N)]
Pset = sorted(set(P))
YMAX = 1400

def match_atlas(tmpl, topk=3):
    th, tw = tmpl.shape
    t = tmpl - tmpl.mean()
    tn = np.sqrt((t * t).sum()) + 1e-6
    n = th * tw
    tmean = tmpl.mean()
    out = []
    for cx in Pset:
        if cx + tw > 2048:
            continue
        col = AT[0:YMAX, cx:cx + tw]
        sw = np.lib.stride_tricks.sliding_window_view(col, (th, tw))[:, 0]
        prod = (sw * t).sum(axis=(1, 2))
        rs = col.sum(axis=1); rs2 = (col * col).sum(axis=1)
        cs = np.concatenate([[0.0], np.cumsum(rs)])
        cs2 = np.concatenate([[0.0], np.cumsum(rs2)])
        yidx = np.arange(prod.shape[0])
        W = cs[yidx + th] - cs[yidx]; W2 = cs2[yidx + th] - cs2[yidx]
        sc = (prod - W * tmean) / (np.sqrt(np.maximum(W2 - W * W / n, 0)) * tn + 1e-6)
        k = int(np.argmax(sc))
        out.append((float(sc[k]), cx, int(yidx[k])))
    out.sort(reverse=True)
    return out[:topk]

print("=== 自检: 取图集 (x=125,y=907) 30x30 作为模板 ===")
t0 = AT[907:907 + 30, 125:125 + 30]
for s, cx, y in match_atlas(t0):
    print("   score=%.3f x=%d y=%d" % (s, cx, y))

print("\n=== 自检2: 取 (x=807,y=194) 30x30 ===")
t1 = AT[194:224, 807:837]
for s, cx, y in match_atlas(t1):
    print("   score=%.3f x=%d y=%d" % (s, cx, y))

# 字幕字形: 直接取 (790,699) 31x28 并尝试多缩放
im = Image.open(r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg').convert('L')
g = np.asarray(im).astype(np.float32)
bg = np.asarray(im.filter(ImageFilter.BoxBlur(11))).astype(np.float32)
ink = np.clip(g - bg, 0, 255)

print("\n=== 字幕第1字形 (任) 多尺度匹配 ===")
for name, box in (('h28', (790, 699, 821, 727)), ('h31', (789, 698, 821, 729)),
                  ('h34', (788, 697, 822, 731))):
    t = ink[box[1]:box[3], box[0]:box[2]]
    for sc in (0.75, 0.85, 0.95, 1.0, 1.05, 1.15):
        h = max(8, int(round(t.shape[0] * sc))); w = max(8, int(round(t.shape[1] * sc)))
        ti = np.asarray(Image.fromarray(t.astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(np.float32)
        r = match_atlas(ti, 1)[0]
        print("   %s scale=%.2f size=%dx%d -> score=%.3f x=%d y=%d" % (name, sc, h, w, r[0], r[1], r[2]))
