import os, sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4)) + [0]*(N-nV)
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
probe = "一二三四五六七八九十日月山川口田人中大小上下左右"
pidx = [cn.index(ord(c)) for c in probe]
print("probe 索引: %s" % pidx)
print()
# 对每个偏移出图
rows_img = []
offs = [-5, 0, 5]
for k in offs:
    tiles = []
    for i in pidx:
        j = i + k
        if not (0 <= j < N): 
            tiles = None; break
        x, y = U[j], V[j]
        g = al[y:y+28, x:x+31]
        if g.shape != (28,31):
            pad = np.zeros((28,31),np.uint8); pad[:g.shape[0],:g.shape[1]] = g; g = pad
        tiles.append(g); tiles.append(np.full((28,3),128,np.uint8))
    if tiles:
        rows_img.append(np.concatenate(tiles, axis=1))
W = max(r.shape[1] for r in rows_img)
padded = []
for k, r in zip(offs, rows_img):
    if r.shape[1] < W:
        r = np.pad(r, ((0,0),(0,W-r.shape[1])), constant_values=200)
    padded.append(r); padded.append(np.full((6,W),100,np.uint8))
s = np.concatenate(padded, axis=0)
Image.fromarray(255-s).resize((s.shape[1]*7, s.shape[0]*7), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\offset3.png")
print("写出 offset3.png，三行偏移依次: %s" % offs)
print("期望每行: %s" % probe)
print()
# ASCII 锚点：索引 0..31 用什么偏移读出来是对的
print("=== ASCII 锚点检验 ===")
for k in (0, 5):
    s2 = "".join(chr(cn[i]) for i in range(32))
    print("  偏移 %+d 时，索引 0..31 读作: %s" % (k, s2))
