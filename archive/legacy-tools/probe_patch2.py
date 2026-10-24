"""严谨探测：patch 图集与 charlist_CH 是否一一对应？

修正之前的错误：不要用「索引 % 66」算网格，直接用 vf3 的 U/V。
本次取一批特征字，逐个记录 (索引, U, V, 行内序号) 并出图。
"""
import os, sys, struct, collections
import numpy as np
from PIL import Image

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"
os.makedirs(OUT, exist_ok=True)


def load(path_vpp, name="fnt_chinese"):
    v = Vpp(path_vpp)
    vf3 = bytes(v.read(v.find(name, "vf3_pc")))
    N = struct.unpack_from("<i", vf3, 0x08)[0]
    U0 = 0xD0 + N * 16
    U = list(struct.unpack_from("<%di" % N, vf3, U0))
    nV = (len(vf3) - (U0 + N * 4)) // 4
    V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
    return v, N, U, V


vp, Np, Up, Vp = load(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in vp.read(vp.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
_, al_p = dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)
print("patch: N=%d, charlist=%d" % (Np, len(cn)))

probe = "一二三四五六七八九十日月山川口田人中大小上下左右你我他们的保护"
idx = [cn.index(ord(c)) for c in probe if ord(c) in cn]
print("探测 %d 字: %s" % (len(idx), probe))
print()

CELL_W, CELL_H = 31, 28
tiles = []
info = []
for i in idx:
    x, y = Up[i], Vp[i]
    g = al_p[y:y + CELL_H, x:x + CELL_W]
    if g.shape != (CELL_H, CELL_W):
        pad = np.zeros((CELL_H, CELL_W), np.uint8)
        pad[:g.shape[0], :g.shape[1]] = g
        g = pad
    tiles.append(g)
    tiles.append(np.full((CELL_H, 2), 255, np.uint8))
    info.append((i, chr(cn[i]), x, y))
s = np.concatenate(tiles, axis=1)
Image.fromarray(255 - s).resize((s.shape[1] * 6, s.shape[0] * 6), Image.NEAREST).save(
    os.path.join(OUT, "probe_patch.png"))
print("写出 probe_patch.png")
print("  idx:   %s" % [i for i, _, _, _ in info])
print("  字表:  %s" % " ".join(ch for _, ch, _, _ in info))
print("  U:     %s" % [x for _, _, x, _ in info])
print("  V:     %s" % [y for _, _, _, y in info])
