# -*- coding: utf-8 -*-
"""把 fnt_chinese 图集渲染成 PNG"""
from PIL import Image
import sys

raw = open(r'F:\sr2-cn\_fontdump\fnt_chinese.tex', 'rb').read()
print("tex size", len(raw))
W = H = 2048
assert len(raw) == W * H, (len(raw), W*H)

im = Image.frombytes('L', (W, H), raw)
im.save(r'F:\sr2-cn\_fontdump\atlas_full.png')
print("saved atlas_full.png", im.size, "extrema", im.getextrema())

# 统计非零像素
hist = im.histogram()
nz = sum(hist[1:])
print("non-zero px:", nz, " max val:", max(i for i, c in enumerate(hist) if c))

# 找出内容包围盒（按行/列的非零投影）
import numpy as np
a = np.frombuffer(raw, dtype=np.uint8).reshape(H, W)
rows = (a > 0).sum(axis=1)
cols = (a > 0).sum(axis=0)
nzr = [i for i, v in enumerate(rows) if v > 0]
nzc = [i for i, v in enumerate(cols) if v > 0]
print("rows with content: %d .. %d (%d)" % (nzr[0], nzr[-1], len(nzr)))
print("cols with content: %d .. %d (%d)" % (nzc[0], nzc[-1], len(nzc)))

# 检测规则网格：找列投影的“空列”周期
empty_cols = [i for i, v in enumerate(cols) if v == 0]
print("empty col count:", len(empty_cols), "first 40:", empty_cols[:40])
empty_rows = [i for i, v in enumerate(rows) if v == 0]
print("empty row count:", len(empty_rows), "first 40:", empty_rows[:40])
