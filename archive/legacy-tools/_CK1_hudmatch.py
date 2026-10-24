# -*- coding: utf-8 -*-
"""HUD 字形 vs 图集 匹配"""
from PIL import Image, ImageFilter
import numpy as np, struct

S2 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T08-17-55-901Z-fad3050f.jpg'
AT = np.frombuffer(open(r'F:\sr2-cn\_fontdump\fnt_chinese.tex', 'rb').read(),
                   dtype=np.uint8).reshape(2048, 2048).astype(np.float32)
d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795; B = 0xBC + N * 16
P = [struct.unpack_from('<I', d, B + i * 8)[0] for i in range(N)]
Pset = sorted(set(P))
YMAX = 1400

def match(tmpl, topk=3):
    th, tw = tmpl.shape
    t = tmpl - tmpl.mean(); tn = np.sqrt((t * t).sum()) + 1e-6; n = th * tw
    tmean = tmpl.mean(); out = []
    for cx in Pset:
        if cx + tw > 2048: continue
        col = AT[0:YMAX, cx:cx + tw]
        sw = np.lib.stride_tricks.sliding_window_view(col, (th, tw))[:, 0]
        prod = (sw * t).sum(axis=(1, 2))
        rs = col.sum(axis=1); rs2 = (col * col).sum(axis=1)
        cs = np.concatenate([[0.0], np.cumsum(rs)]); cs2 = np.concatenate([[0.0], np.cumsum(rs2)])
        yidx = np.arange(prod.shape[0])
        W = cs[yidx + th] - cs[yidx]; W2 = cs2[yidx + th] - cs2[yidx]
        sc = (prod - W * tmean) / (np.sqrt(np.maximum(W2 - W * W / n, 0)) * tn + 1e-6)
        k = int(np.argmax(sc)); out.append((float(sc[k]), cx, int(yidx[k])))
    out.sort(reverse=True)
    return out[:topk]

im = Image.open(S2).convert('L')
g = np.asarray(im).astype(np.float32)
# HUD 文字为亮白，面板为暗色: 直接用亮度减局部暗底
ink = np.clip(g - 60.0, 0, 255)

print("=== HUD '直升机突击' 各字形匹配 ===")
# 直 升 机 突 击 大约 pitch 25, 起点 x=216, y 95..125
for i, ch in enumerate('直升机突击'):
    x0 = 215 + int(round(i * 25.2))
    t = ink[94:126, x0:x0 + 27]
    Image.fromarray(t.astype(np.uint8)).save(r'F:\sr2-cn\_glyphs\hud_%d.png' % i)
    res = match(t)
    print("  %s  x=%d  ->  %s" % (ch, x0, ", ".join("score=%.3f (x=%d,y=%d)" % r for r in res)))

print("\n=== HUD '面包车耐久' ===")
for i, ch in enumerate('面包车耐久'):
    x0 = 215 + int(round(i * 25.2))
    t = ink[140:172, x0:x0 + 27]
    res = match(t)
    print("  %s  x=%d  ->  %s" % (ch, x0, ", ".join("score=%.3f (x=%d,y=%d)" % r for r in res)))
