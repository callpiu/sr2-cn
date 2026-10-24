# -*- coding: utf-8 -*-
# 假设检验：图集B(textures.fnt_chinese.) 的 cell[371] 是否画的是「任」？
import struct, sys
import numpy as np
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
CELL = 31

vp = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
vf = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
U = list(struct.unpack_from("<%di" % N, vf, 0xAF6C))
V = list(struct.unpack_from("<%di" % N, vf, 0xDB18))
_, alphaA = dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)

vt = Vpp(G + r"\textures.vpp_pc")
ent = vt.find("fnt_chinese")  # 无扩展名那个 4MB
raw = bytes(vt.read(ent))
print(f"textures fnt_chinese: size={len(raw)}")
_, alphaB = dxt3_decode(raw, 2048, 2048)

def cell(img, i):
    x, y = U[i], V[i]
    return img[y:y+28, x:x+CELL].astype(np.int16)

def diff(a, b):
    if a.shape != b.shape:
        return 9999
    return int(np.abs(a - b).mean())

idx_of = {}
for i, c in enumerate(CPS):
    idx_of.setdefault(c, i)

# 待验证映射: 真idx -> 疑似屏字idx
tests = [("你", 371, 336), ("的", 1836, 1784), ("们", 332, 362),
         ("保", 391, 354), ("他", 324, 301), ("击", 479, 458), ("去", 581, 535)]
print(f"{'真字':>4} {'真idx':>5} -> {'屏字':>4} {'屏idx':>5} | A内自比 B[真]vsA[屏] B[真]vsA[真]")
for ch, ti, si in tests:
    caT, caS = cell(alphaA, ti), cell(alphaA, si)
    cbT = cell(alphaB, ti)
    d_cross = diff(cbT, caS)   # 图集B的[真idx] vs 图集A的[屏字idx]
    d_same  = diff(cbT, caT)   # 图集B的[真idx] vs 图集A的[真idx] (应大=不同图)
    print(f"{ch} {ti:>5} -> {ch} {si:>5} | cross={d_cross:>4}  same={d_same:>4}")
