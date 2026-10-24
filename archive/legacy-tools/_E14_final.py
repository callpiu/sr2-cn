# -*- coding: utf-8 -*-
"""★★★ 最终判定：patch vf3 的 U/V 是【像素坐标】且 100% 对齐【patch/汉化图集】

patch vf3: 格距 31，起点 (1,1)。i=0 -> (1,1)；i=2 -> (32,1)；i=224 -> (1458,32)
=> 第 47 列第 1 行 —— 完美整数格。

⇒ 结论：**patch.vpp_pc 里的 (vf3 + g_peg_pc图集) 是一对自洽的字体**
   而 common.vpp_pc 的 vf3 用的是【另一套网格/图集】（180+ 字形行距 18，CJK 行距 30）

现在做最后一击：用 patch vf3 的 slot 索引，从 patch 图集取图，
               看能否重现 真机看到的乱码字 或 正确字。
"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_vf3(path):
    v = Vpp(path); e = v.find("fnt_chinese", "vf3_pc"); o = v.data_start + e['body']
    N = struct.unpack_from('<I', v.data, o + 8)[0]
    ro, uo, vo = 0xBC, 0xBC + N*16, 0xBC + N*16 + N*4
    R = [struct.unpack_from('<4H', v.data, o+ro+i*16) for i in range(N)]
    U = [struct.unpack_from('<H', v.data, o+uo+i*2)[0] for i in range(N)]
    V = [struct.unpack_from('<H', v.data, o+vo+i*2)[0] for i in range(N)]
    return R, U, V, N

RP, UP, VP, NP = load_vf3(os.path.join(G, "patch.vpp_pc"))
RC, UC, VC, NC = load_vf3(os.path.join(G, "common.vpp_pc"))

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
A_HAN = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
A_TEX = vt.read(next(x for x in vt.entries() if x['name'] == 'fnt_chinese'))
_, PH = dxt3_decode(A_HAN, 2048, 2048)
_, PT = dxt3_decode(A_TEX, 2048, 2048)

CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
s2i = {chr(cp): i + 0x20 for i, cp in enumerate(CL)}
c2s = {chr(cp): i + 0x20 for i, cp in enumerate(CL)}

def cell(alp, U, V, s, size=31):
    if s < 0 or s >= len(U): return np.zeros((size, size), 'uint8')
    uu, vv = U[s], V[s]
    if uu + size > 2048 or vv + size > 2048: return np.zeros((size, size), 'uint8')
    return alp[vv:vv+size, uu:uu+size]

def strip(alp, U, V, slots, size=31):
    return np.hstack([np.pad(cell(alp, U, V, s, size), ((2,2),(2,2))) for s in slots])

CORRECT = "你的弟兄们需要你的保护"
slots = [c2s[ch] for ch in CORRECT]

rows = [
    ("patch表(pixel U/V) + patch/汉化图集", strip(PH, UP, VP, slots)),
    ("patch表(pixel U/V) + textures官方图集", strip(PT, UP, VP, slots)),
    ("common表 + textures官方图集",         strip(PT, UC, VC, slots)),
    ("common表 + 汉化图集",                 strip(PH, UC, VC, slots)),
]
W = max(r[1].shape[1] for r in rows); H = sum(r[1].shape[0]+12 for r in rows)+8
cv = np.zeros((H, W+8), 'uint8'); y = 4
for lab, a in rows:
    cv[y:y+a.shape[0], 4:4+a.shape[1]] = a
    y += a.shape[0]+12
Image.fromarray(cv).save(r"F:\sr2-cn\_E14_final_pairing.png")
print("写出 _E14_final_pairing.png")
for i, (lab, a) in enumerate(rows):
    print("  行%d: %s" % (i, lab))

# 关键：patch 图集 与 patch vf3 是否真的一一对应？
# 用 patch 的 ASCII 段验证：idx 0..25 应画出 !"#$%...
print("\n验证 patch 表 + patch 图集 的 ASCII 段 idx 0..25:")
a = strip(PH, UP, VP, list(range(26)))
Image.fromarray(np.kron(a, np.ones((3,3),'uint8'))).save(r"F:\sr2-cn\_E15_patch_ascii.png")
print("  写出 _E15_patch_ascii.png")
