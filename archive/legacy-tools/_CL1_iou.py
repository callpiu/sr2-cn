# -*- coding: utf-8 -*-
"""二值化 IoU 匹配（对反锯齿更鲁棒）"""
from PIL import Image, ImageFilter
import numpy as np, struct

AT = np.frombuffer(open(r'F:\sr2-cn\_fontdump\fnt_chinese.tex', 'rb').read(),
                   dtype=np.uint8).reshape(2048, 2048)
ATB = (AT > 110).astype(np.float32)          # 图集二值
d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795; B = 0xBC + N * 16
P = [struct.unpack_from('<I', d, B + i * 8)[0] for i in range(N)]
Pset = sorted(set(P))

def iou_match(tmpl_b, topk=5):
    th, tw = tmpl_b.shape
    tb = (tmpl_b > 0).astype(np.float32)
    tn = tb.sum()
    out = []
    for cx in Pset:
        if cx + tw > 2048: continue
        col = ATB[0:1400, cx:cx + tw]
        sw = np.lib.stride_tricks.sliding_window_view(col, (th, tw))[:, 0]
        inter = (sw * tb).sum(axis=(1, 2))
        wsum = sw.sum(axis=(1, 2))
        union = wsum + tn - inter
        iou = inter / np.maximum(union, 1)
        k = int(np.argmax(iou))
        out.append((float(iou[k]), cx, k))
    out.sort(reverse=True)
    return out[:topk]

im = Image.open(r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg').convert('L')
g = np.asarray(im).astype(np.float32)
bg = np.asarray(im.filter(ImageFilter.BoxBlur(11))).astype(np.float32)
ink = g - bg

print("=== 字幕 11 字形 IoU 匹配 (阈值: ink>25) ===")
x0, pitch = 790, 31.18
for i in range(11):
    a = int(round(x0 + i * pitch)); b = int(round(x0 + (i + 1) * pitch))
    t = (ink[699:727, a:b] > 25).astype(np.float32)
    if t.sum() < 10:
        print("  #%d 空" % i); continue
    res = iou_match(t)
    print("  #%-2d 模板墨点数=%-4d -> %s" % (i, int(t.sum()),
          ", ".join("IoU=%.3f (x=%d,y=%d)" % r for r in res[:3])))

# 自检: 图集某格
print("\n=== 自检 (图集 x=807 y=194 30x30) ===")
t0 = ATB[194:224, 807:837].astype(np.float32)
for r in iou_match(t0, 3):
    print("   IoU=%.3f (x=%d,y=%d)" % r)
