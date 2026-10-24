# -*- coding: utf-8 -*-
"""按候选网格假设裁剪单格并放大"""
from PIL import Image
im = Image.open(r'F:\sr2-cn\_fontdump\atlas_full.png')

def cell(name, idx, cols=64, cw=32, ch=30, oy=8, scale=14, pad=4):
    c = idx % cols
    r = idx // cols
    x = c * cw
    y = oy + r * ch
    box = (max(0, x - pad), max(0, y - pad), x + cw + pad, y + ch + pad)
    g = im.crop(box).resize(((box[2]-box[0]) * scale, (box[3]-box[1]) * scale), Image.NEAREST)
    g.save(r'F:\sr2-cn\_fontdump\%s.png' % name)
    print("saved %s  idx=%d -> col=%d row=%d box=%s" % (name, idx, c, r, box))

# 假设: 64 列, 32x30, 起点 y=8
for i in (403, 1887, 582, 364, 1868, 423, 0, 1, 2, 224):
    cell('g32_%d' % i, i, 64, 32, 30, 8, 14)

# 假设: 64 列, 32x32, 起点 y=0
for i in (403, 1887):
    cell('g32b_%d' % i, i, 64, 32, 32, 0, 14)
