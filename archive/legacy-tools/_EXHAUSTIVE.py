# -*- coding: utf-8 -*-
"""穷举：找出游戏实际使用的 (vf3, 图集) 组合
目标：复现游戏截图里的乱码 "任璨偶巧位雄衡任璨伪该"
"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
RO = 0xBC
REF = "F:/sr2-cn/_ref92/黑道圣徒2简体汉化补丁/patch.vpp_pc"
OFFP = "F:/sr2-cn/SR2_简体中文补丁_v8/backup_original/patch.vpp_pc"
OFFC = "F:/sr2-cn/_backup_F/common.official_20261013_175139.vpp_pc"


def vf3_of(p, name='fnt_chinese'):
    v = Vpp(p); b = v.read(v.find(name, "vf3_pc")); del v
    N = struct.unpack_from('<I', b, 8)[0]
    uo = RO + N * 16; vo = uo + N * 4
    return dict(N=N,
                U=[struct.unpack_from('<I', b, uo + i * 4)[0] for i in range(N)],
                V=[struct.unpack_from('<I', b, vo + i * 4)[0] for i in range(N)])


def atlas_by(p, gpeg=True):
    v = Vpp(p)
    e = v.find("fnt_chinese", "g_peg_pc") if gpeg else next(x for x in v.entries() if x['name'] == 'fnt_chinese')
    b = v.read(e); del v
    return dxt3_decode(b, 2048, 2048)[1]


VF_CUR = vf3_of(os.path.join(G, "patch.vpp_pc"))
VF_REF = vf3_of(REF)
VF_OFF = vf3_of(OFFC)

A_CN = atlas_by(os.path.join(G, "patch.vpp_pc"), True)          # 34034076 汉化
A_TEX = atlas_by(os.path.join(G, "textures.vpp_pc"), False)     # 现在=34034076
A_OFFP = atlas_by(OFFP, True)                                   # a8c33f12 官方patch
A_OFFT = atlas_by("F:/sr2-cn/_backup_I/textures.before_atlas_fix_20261014.vpp_pc", False)  # 62a57046 官方textures

v = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in v.read(v.find("charlist_CH", "txt")).replace(b"\r\n", b"\n").split(b"\n") if s.strip().isdigit()]
del v
c2i = {chr(cp): i for i, cp in enumerate(CL)}

TEXT = "你的弟兄们需要你的保护"
SZ = 32


def strip(alp, T, off):
    cells = []
    for ch in TEXT:
        j = c2i[ch] + off
        if j < 0 or j >= T['N'] or T['U'][j] + SZ > 2048 or T['V'][j] + SZ > 2048:
            cells.append(np.zeros((SZ, SZ), 'uint8')); continue
        uu, vv = T['U'][j], T['V'][j]
        cells.append(np.pad(alp[vv:vv + SZ, uu:uu + SZ], ((2, 2), (2, 2))))
    return np.hstack(cells)


combos = [
    ("汉化图集34034076 + 当前vf3(2795)", A_CN, VF_CUR, 0),
    ("官方tex图集62a57046 + 当前vf3(2795)", A_OFFT, VF_CUR, 0),
    ("官方patch图集a8c33f12 + 当前vf3(2795)", A_OFFP, VF_CUR, 0),
    ("汉化图集34034076 + 官方vf3(2838)", A_CN, VF_OFF, 0),
    ("官方tex图集62a57046 + 官方vf3(2838)", A_OFFT, VF_OFF, 0),
    ("汉化图集34034076 + 官方vf3(2838) slot+32", A_CN, VF_OFF, 32),
    ("汉化图集34034076 + 当前vf3 slot+32", A_CN, VF_CUR, 32),
]
rows = []
for lab, a, t, off in combos:
    rows.append((lab, strip(a, t, off)))

W = max(r.shape[1] for _, r in rows)
H = sum(r.shape[0] + 12 for _, r in rows) + 10
cv = np.zeros((H, W + 10), 'uint8')
y = 5
for lab, r in rows:
    cv[y:y + r.shape[0], 5:5 + r.shape[1]] = r
    y += r.shape[0] + 12
img = Image.fromarray(cv)
img = img.resize((int(img.width * 1.8), int(img.height * 1.8)), Image.NEAREST)
img.save(r"F:\sr2-cn\_EXHAUSTIVE.png")
print("写出 _EXHAUSTIVE.png")
print("目标（游戏截图乱码）: 任璨偶巧位雄衡任璨伪该")
print()
for i, (lab, _) in enumerate(rows):
    print("  行%d: %s" % (i, lab))
