# -*- coding: utf-8 -*-
"""扫描 vf3 索引偏移：找出哪个 j = 槽位 + delta 能渲染出正确中文

目标文本 "你的弟兄们需要你的保护"
"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
RO = 0xBC
REF = "F:/sr2-cn/_ref92/黑道圣徒2简体汉化补丁/patch.vpp_pc"


def load_vf3(b):
    N = struct.unpack_from('<I', b, 8)[0]
    uo = RO + N * 16
    vo = uo + N * 4
    U = [struct.unpack_from('<I', b, uo + i * 4)[0] for i in range(N)]
    V = [struct.unpack_from('<I', b, vo + i * 4)[0] for i in range(N)]
    return dict(U=U, V=V, N=N)


def vf3_of(path):
    v = Vpp(path); b = v.read(v.find("fnt_chinese", "vf3_pc")); del v
    return load_vf3(b)


def atlas_of(path, want_gpeg=True):
    v = Vpp(path)
    e = v.find("fnt_chinese", "g_peg_pc") if want_gpeg else next(x for x in v.entries() if x['name'] == 'fnt_chinese')
    b = v.read(e); del v
    _, px = dxt3_decode(b, 2048, 2048)
    return px


VF_REF = vf3_of(REF)
VF_CUR = vf3_of(os.path.join(G, "patch.vpp_pc"))
A_CN = atlas_of(os.path.join(G, "patch.vpp_pc"))
A_TEX = atlas_of(os.path.join(G, "textures.vpp_pc"), want_gpeg=False)

v = Vpp(REF)
CL = [int(s) for s in v.read(v.find("charlist_CH", "txt")).replace(b"\r\n", b"\n").split(b"\n") if s.strip().isdigit()]
del v
c2i = {chr(cp): i for i, cp in enumerate(CL)}
TEXT = "你的弟兄们需要你的保护"
idx = [c2i[ch] for ch in TEXT]
print("charlist 索引:", idx)

SIZE = 32


def cell(alp, T, j, size=SIZE):
    if j < 0 or j >= len(T['U']):
        return np.zeros((size, size), 'uint8')
    uu, vv = T['U'][j], T['V'][j]
    if uu + size > 2048 or vv + size > 2048:
        return np.zeros((size, size), 'uint8')
    return alp[vv:vv + size, uu:uu + size]


def row(alp, T, js):
    return np.hstack([np.pad(cell(alp, T, j), ((1, 1), (2, 2))) for j in js])


rows = []
labels = []
for delta in range(-6, 7):
    js = [i + delta for i in idx]
    rows.append(row(A_CN, VF_REF, js)); labels.append("汉化图集+基准vf3  j=idx%+d" % delta)
# 再用官方图集试几个
for delta in (0, -5):
    js = [i + delta for i in idx]
    rows.append(row(A_TEX, VF_REF, js)); labels.append("官方图集+基准vf3  j=idx%+d" % delta)

W = max(r.shape[1] for r in rows)
H = sum(r.shape[0] + 8 for r in rows) + 8
cv = np.zeros((H, W + 8), 'uint8')
y = 4
for r in rows:
    cv[y:y + r.shape[0], 4:4 + r.shape[1]] = r
    y += r.shape[0] + 8
img = Image.fromarray(cv)
img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
img.save(r"F:\sr2-cn\_SCAN_index_offset.png")
print("\n写出 _SCAN_index_offset.png")
for i, l in enumerate(labels):
    print("   行%d: %s" % (i, l))
