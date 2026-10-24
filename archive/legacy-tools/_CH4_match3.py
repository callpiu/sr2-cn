# -*- coding: utf-8 -*-
"""向量化模板匹配：字幕字形 -> 图集坐标"""
from PIL import Image, ImageFilter
import numpy as np, os, struct

S1 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg'
OUT = r'F:\sr2-cn\_glyphs'
os.makedirs(OUT, exist_ok=True)

AT = np.frombuffer(open(r'F:\sr2-cn\_fontdump\fnt_chinese.tex', 'rb').read(),
                   dtype=np.uint8).reshape(2048, 2048).astype(np.float32)

d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
B = 0xBC + N * 16
P = [struct.unpack_from('<I', d, B + i * 8)[0] for i in range(N)]
Pset = sorted(set(P))

im = Image.open(S1).convert('L')
g = np.asarray(im).astype(np.float32)
bg = np.asarray(im.filter(ImageFilter.BoxBlur(7))).astype(np.float32)
ink = np.clip(g - bg, 0, 255)

band = ink[690:745, 700:1350]
cp = (band > 90).sum(axis=0)
xs = [x for x, v in enumerate(cp) if v > 0]
x0, x1 = xs[0] + 700, xs[-1] + 700
rp = (ink[690:745, x0:x1 + 1] > 90).sum(axis=1)
ys = [y for y, v in enumerate(rp) if v > 0]
ty, by = ys[0] + 690, ys[-1] + 690
NC = 11
pitch = (x1 - x0 + 1) / NC
print("字幕 x %d..%d y %d..%d pitch %.2f" % (x0, x1, ty, by, pitch))

YMAX = 1400

def match(tmpl, topk=5):
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
        rs = col.sum(axis=1)
        rs2 = (col * col).sum(axis=1)
        cs = np.concatenate([[0.0], np.cumsum(rs)])
        cs2 = np.concatenate([[0.0], np.cumsum(rs2)])
        nw = prod.shape[0]
        yidx = np.arange(nw)
        W = cs[yidx + th] - cs[yidx]
        W2 = cs2[yidx + th] - cs2[yidx]
        num = prod - W * tmean
        den = np.sqrt(np.maximum(W2 - W * W / n, 0)) * tn + 1e-6
        sc = num / den
        k = int(np.argmax(sc))
        out.append((float(sc[k]), cx, int(yidx[k])))
    out.sort(reverse=True)
    return out[:topk]

print()
for i in range(NC):
    a = int(round(x0 + i * pitch))
    b = int(round(x0 + (i + 1) * pitch))
    tmpl = ink[ty:by + 1, a:b]
    Image.fromarray(tmpl.astype(np.uint8)).save(os.path.join(OUT, 'c_%02d.png' % i))
    res = match(tmpl)
    idxs = [k for k in range(N) if P[k] == res[0][1]]
    print("#%-2d 最佳 atlas=(x=%d,y=%d) score=%.3f  -> glyph idx 候选 %s" %
          (i, res[0][1], res[0][2], res[0][0], idxs[:8]))
    print("    其他: " + ", ".join("(x=%d,y=%d,%.3f)" % (c, y, s) for s, c, y in res[1:]))
