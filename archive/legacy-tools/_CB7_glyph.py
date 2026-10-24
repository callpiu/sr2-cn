# -*- coding: utf-8 -*-
"""按破译的图集布局精确裁剪字形"""
from PIL import Image
import struct

im = Image.open(r'F:\sr2-cn\_fontdump\atlas_full.png')
d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
B = 0xBC + N * 16

def pos(i):
    r = i // 65
    j = i % 65
    col = 2 * j if j < 33 else 2 * (j - 33) + 1
    x = 1 + 31 * col
    y = 8 + 31 * r
    return x, y

# 校验: P 是否等于 x
bad = 0
for i in range(N):
    p, q = struct.unpack_from('<2I', d, B + i * 8)
    x, y = pos(i)
    if p != x:
        bad += 1
        if bad < 6:
            print("  不匹配 i=%d P=%d 公式x=%d" % (i, p, x))
print("P 与公式 x 不匹配数:", bad, "/", N)

def crop(name, idx, scale=16):
    x, y = pos(idx)
    g = im.crop((x - 2, y - 2, x + 33, y + 33))
    g = g.resize((35 * scale, 35 * scale), Image.NEAREST)
    g.save(r'F:\sr2-cn\_fontdump\%s.png' % name)
    print("saved %-14s idx=%-5d -> (%d, %d) row=%d" % (name, idx, x, y, idx // 65))

for idx in (403, 1887, 582, 364, 1868, 423, 1447, 511, 0, 1, 2, 3):
    crop('k_%d' % idx, idx)

# 同时导出一整行的拼接图便于批量阅读
def rowimg(name, row, scale=4):
    y = 8 + 31 * row
    g = im.crop((0, y, 2048, y + 31))
    g = g.resize((2048 * scale // 4, 31 * scale // 4), Image.NEAREST)
    g.save(r'F:\sr2-cn\_fontdump\%s.png' % name)
    print("saved", name, "row", row, "y", y)

rowimg('R6', 6)
rowimg('R29', 29)
