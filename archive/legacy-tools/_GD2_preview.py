# -*- coding: utf-8 -*-
"""GD2: 预览 —— 用修复后的 fnt_body_n 字体数据, 把这两条字幕应有的样子渲染出来。"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_GD2_preview.png"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
T = [int(s) for s in v.read(v.find("charlist_CH","txt")).decode("utf-8","replace").replace("\r","\n").split("\n") if s.strip().isdigit()]
IDX = {c:i for i,c in enumerate(T)}

t = Vpp(os.path.join(G, "textures.vpp_pc"))
rgb, A = dxt3_decode(t.read(t.find("fnt_body_n")), 2048, 2048)   # 修复后的 fnt_body_n 图集
print("fnt_body_n 图集:", A.shape, "alpha max", int(A.max()))

PITCH, COLS = 31, 65
def cell(i):
    r_, c_ = i//COLS, i%COLS
    return A[1+PITCH*r_:1+PITCH*r_+PITCH, 1+PITCH*c_:1+PITCH*c_+PITCH]

LINES = [
    ("SUB1", "你的弟兄们需要你的保护", 8),
    ("SUB3", "你的弟兄们要出去谈几笔生意，保护他们免遭袭击", 8),
]
Z = 6
tiles = []
for tag, s, _ in LINES:
    row = [np.zeros((PITCH, 10), np.uint8)]
    for ch in s:
        i = IDX[ord(ch)]
        row.append(cell(i))
        row.append(np.zeros((PITCH, 3), np.uint8))
    tiles.append(np.concatenate(row, axis=1))
    print("%s  槽位: %s" % (tag, [IDX[ord(c)] for c in s]))

W = max(t.shape[1] for t in tiles)
padded = []
for t_ in tiles:
    pad = np.zeros((PITCH, W - t_.shape[1]), np.uint8)
    padded.append(np.concatenate([t_, pad], axis=1))
    padded.append(np.zeros((8, W), np.uint8))
img = np.concatenate(padded[:-1], axis=0)
img = np.kron(img, np.ones((Z, Z), np.uint8))
Image.fromarray(img, "L").save(OUT)
print("已保存", OUT, img.shape)
