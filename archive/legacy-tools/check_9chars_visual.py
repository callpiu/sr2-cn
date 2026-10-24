# -*- coding: utf-8 -*-
"""决定性验证: 把9个乱码字/正确字 在 patch表 与 common表 下的索引, 各自渲染图集字形"""
import os, sys, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def load_table(vppn, name="charlist_CH"):
    v = Vpp(os.path.join(G, vppn))
    e = v.find(name, "txt")
    buf = v.read(e)
    end = buf.find(b'//ENDOFFILE')
    if end < 0: end = len(buf)
    import re
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]

def load_uv(vppn):
    v = Vpp(os.path.join(G, vppn))
    vf3 = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
    N = struct.unpack_from("<i", vf3, 0x08)[0]
    U0 = 0xD0 + N * 16
    U = list(struct.unpack_from("<%di" % N, vf3, U0))
    nV = (len(vf3) - (U0 + N * 4)) // 4
    V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
    return N, U, V

# 图集(用 patch 的 g_peg_pc = 与 textures 的 4MB 一致)
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
_, atlas = dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)

cur = load_table("patch.vpp_pc")      # 2795
off = load_table("../../F:/sr2-cn/pristine/patch.vpp_pc")  # will redo below

# common 表(2838)在对应用 common 的 vf3; 这里先试 common.vf3 与 patch 表
Np, Up, Vp_ = load_uv("patch.vpp_pc")
print("patch vf3 N=%d" % Np)

def tile(U, V, i, h=28, w=31):
    x, y = U[i], V[i]
    g = atlas[y:y+h, x:x+w]
    if g.shape != (h, w):
        pad = np.zeros((h, w), np.uint8); pad[:g.shape[0], :g.shape[1]] = g; g = pad
    return g

targets = ["你","的","弟","兄","们","需","要","保","护"]
disp    = ["任","璨","偶","巧","位","雄","衡","伪","该"]

# 用 patch 表的索引, patch vf3 的 UV
print("=== patch表idx + patch vf3 UV ===")
tiles = []
labels = []
for k, ch in enumerate(targets):
    i = cur.index(ord(ch))
    tiles.append(tile(Up, Vp_, i)); tiles.append(np.full((28,2),255,np.uint8))
    labels.append("%s(%d)"%(ch,i))
    # 乱码字也在 patch 表找索引
    j = cur.index(ord(disp[k]))
    tiles.append(tile(Up, Vp_, j)); tiles.append(np.full((28,4),128,np.uint8))
    labels.append("%s(%d)"%(disp[k],j))
s = np.concatenate(tiles, axis=1)
out = "/".join(s.split("/")[:-1]) + "/_verify_9patch.png"
Image.fromarray(255-s).resize((s.shape[1]*6, s.shape[0]*6), Image.NEAREST).save(out)
print("写出", out)
print("顺序:", labels)
