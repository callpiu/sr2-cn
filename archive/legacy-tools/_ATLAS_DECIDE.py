# -*- coding: utf-8 -*-
"""干净对照：同一索引、同一vf3，只换图集"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
RO = 0xBC
REF = "F:/sr2-cn/_ref92/黑道圣徒2简体汉化补丁/patch.vpp_pc"


def vf3_of(p):
    v = Vpp(p); b = v.read(v.find("fnt_chinese", "vf3_pc")); del v
    N = struct.unpack_from('<I', b, 8)[0]
    uo = RO + N * 16; vo = uo + N * 4
    return dict(N=N,
                U=[struct.unpack_from('<I', b, uo + i * 4)[0] for i in range(N)],
                V=[struct.unpack_from('<I', b, vo + i * 4)[0] for i in range(N)])


def atlas(path, gpeg):
    v = Vpp(path)
    e = v.find("fnt_chinese", "g_peg_pc") if gpeg else next(x for x in v.entries() if x['name'] == 'fnt_chinese')
    b = v.read(e); del v
    return dxt3_decode(b, 2048, 2048)[1]


VF = vf3_of(REF)
A_CN = atlas(os.path.join(G, "patch.vpp_pc"), True)
A_TEX = atlas(os.path.join(G, "textures.vpp_pc"), False)

v = Vpp(REF)
CL = [int(s) for s in v.read(v.find("charlist_CH", "txt")).replace(b"\r\n", b"\n").split(b"\n") if s.strip().isdigit()]
del v
c2i = {chr(cp): i for i, cp in enumerate(CL)}

TEXT = "你的弟兄们需要你的保护"
js = [c2i[ch] for ch in TEXT]
SZ = 32


def row(alp):
    cells = []
    for j in js:
        uu, vv = VF['U'][j], VF['V'][j]
        cells.append(np.pad(alp[vv:vv + SZ, uu:uu + SZ], ((3, 3), (3, 3))))
    return np.hstack(cells)


r1 = row(A_CN)
r2 = row(A_TEX)
W = max(r1.shape[1], r2.shape[1])
cv = np.zeros((r1.shape[0] + r2.shape[0] + 24, W + 12), 'uint8')
cv[6:6 + r1.shape[0], 6:6 + r1.shape[1]] = r1
y = r1.shape[0] + 18
cv[y:y + r2.shape[0], 6:6 + r2.shape[1]] = r2
img = Image.fromarray(cv)
img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
img.save(r"F:\sr2-cn\_ATLAS_DECIDE.png")
print("写出 _ATLAS_DECIDE.png")
print("上=汉化图集 34034076  下=官方图集 62a57046")
print("索引 j =", js)
