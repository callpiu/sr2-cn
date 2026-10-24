# -*- coding: utf-8 -*-
"""暴力搜索：引擎用的 (列数 W, 步距 p, 原点 x0,y0) 能否解释全部 9 个 索引->格子 观测。
   模型: 引擎把字形索引 i 映射到像素 (x0+p*(i%W), y0+p*(i//W))，
   而图集真实格距 31、每行 65 格 ⇒ 真实格子 = ((y-1)//31)*65 + ((x-1)//31)。"""
import itertools
OBS = [(371,336),(1836,1784),(1035,410),(422,967),(332,362),
       (2667,2656),(2296,2268),(391,354),(1190,2342)]
best = []
for W in range(32, 130):
    for p in range(20, 40):
        for x0 in range(0, 5):
            for y0 in range(0, 5):
                ok = 0
                for i, cell in OBS:
                    col, row = i % W, i // W
                    x = x0 + p*col; y = y0 + p*row
                    if x < 1 or y < 1: continue
                    tcol = (x-1)//31; trow = (y-1)//31
                    if tcol < 0 or tcol > 64: continue
                    if trow*65 + tcol == cell: ok += 1
                if ok >= 5:
                    best.append((ok, W, p, x0, y0))
best.sort(reverse=True)
print("候选(命中数, 列数W, 步距p, x0, y0):")
for b in best[:20]:
    print("  ", b)
if not best:
    print("  无任何组合命中 >=5 —— 说明不是「网格参数错」这一类错误")
