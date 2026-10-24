# -*- coding: utf-8 -*-
"""裁剪图集局部并放大，用于确定网格与识别字形"""
from PIL import Image
import sys

im = Image.open(r'F:\sr2-cn\_fontdump\atlas_full.png')

def crop(name, x, y, w, h, scale=6):
    c = im.crop((x, y, x+w, y+h))
    c = c.resize((w*scale, h*scale), Image.NEAREST)
    c.save(r'F:\sr2-cn\_fontdump\%s.png' % name)
    print("saved", name, (x, y, w, h), "->", c.size)

crop('c_tl', 0, 0, 192, 192, 6)          # 左上角 6x6 格
crop('c_tl2', 0, 0, 96, 96, 10)          # 左上角 3x3 格
crop('c_row0', 0, 0, 512, 40, 4)         # 第一行
crop('c_col0', 0, 0, 40, 512, 4)         # 第一列
