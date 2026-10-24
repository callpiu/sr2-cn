# -*- coding: utf-8 -*-
"""从 S2 HUD 面板取中文字形，同样做匹配"""
from PIL import Image, ImageFilter
import numpy as np, os, struct

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
bg = np.asarray(im.filter(ImageFilter.BoxBlur(11))).astype(np.float32)
ink = np.clip(g - bg, 0, 255)

# HUD 面板区域
sub = ink[60:115, 140:320]
cp = (sub > 45).sum(axis=0)
xs = [x for x, v in enumerate(cp) if v > 0]
print("HUD 列投影非零 x:", (xs[0] + 140, xs[-1] + 140) if xs else None)
print("cp:", [(140 + x, int(cp[x])) for x in range(0, 180, 4)])
rp = (sub > 45).sum(axis=1)
ys = [y for y, v in enumerate(rp) if v > 0]
print("HUD 行范围:", (ys[0] + 60, ys[-1] + 60) if ys else None)
print("rp:", [(60 + y, int(rp[y])) for y in range(0, 55, 2)])
