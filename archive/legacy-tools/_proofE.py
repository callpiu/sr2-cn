# -*- coding: utf-8 -*-
"""修复 E 视觉证明：REC1 的 slot 序列在【修复前/后】引擎路径下渲染
   修复前引擎图集 = 官方 62a57046…（备份里）
   修复后引擎图集 = 汉化 34034076…
"""
import sys, os, struct, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BAK  = r"F:\sr2-cn\_backup_E"

# 引擎 vf3 = common（2838）
vc = Vpp(os.path.join(GAME, "common.vpp_pc"))
ec = vc.find("fnt_chinese", "vf3_pc")
co = vc.data_start + ec['body']
N = struct.unpack_from('<I', vc.data, co + 8)[0]
UOFF = 0xBC + N*16
VOFF = UOFF + N*4
U = lambda i: struct.unpack_from('<H', vc.data, co + UOFF + i*2)[0]
V = lambda i: struct.unpack_from('<H', vc.data, co + VOFF + i*2)[0]
REC = lambda i: struct.unpack_from('<4H', vc.data, co + 0xBC + i*16)
print("engine vf3 N=%d  UOFF=%#x VOFF=%#x" % (N, UOFF, VOFF))

# 两张图集
atlas_off = None
for f in os.listdir(BAK):
    if f.startswith("textures.official_"):
        atlas_off = os.path.join(BAK, f); break
vt = Vpp(atlas_off)
et = next(x for x in vt.entries() if x['name'] == 'fnt_chinese')
A_OFFICIAL = vt.read(et)
vt2 = Vpp(os.path.join(GAME, "textures.vpp_pc"))
et2 = next(x for x in vt2.entries() if x['name'] == 'fnt_chinese')
A_HAN = vt2.read(et2)
print("官方图集 md5", hashlib.md5(A_OFFICIAL).hexdigest())
print("汉化图集 md5", hashlib.md5(A_HAN).hexdigest())

_, ALP_OFF = dxt3_decode(A_OFFICIAL, 2048, 2048)
_, ALP_HAN = dxt3_decode(A_HAN, 2048, 2048)

REC1 = [403,1868,91,102,111,114,109,97,116,93,91,99,111,108,111,114,58,103,114,101,101,110,93,1067,454,364,91,47,102,111,114,109,97,116,93,2699,2328,403,1868,423,1222]
CJK  = [403,1868,1067,454,364,2699,2328,403,1868,423,1222]

def cell(alp, slot):
    if slot >= N: return np.zeros((32,32),'uint8')
    UU, VV = U(slot), V(slot)
    if VV+32 > 2048 or UU+32 > 2048: return np.zeros((32,32),'uint8')
    return alp[VV:VV+32, UU:UU+32]

def strip(alp, slots):
    return np.hstack([np.pad(cell(alp,s), ((3,3),(3,3))) for s in slots])

rows = [
    ("修复前：common vf3 + 官方图集", strip(ALP_OFF, CJK)),
    ("修复后：common vf3 + 汉化图集", strip(ALP_HAN, CJK)),
]
W = max(r[1].shape[1] for r in rows)
H = sum(r[1].shape[0]+10 for r in rows)+10
cv = np.zeros((H,W),'uint8'); y=0
for lab, s in rows:
    cv[y:y+s.shape[0], :s.shape[1]] = s
    y += s.shape[0]+10
Image.fromarray(cv).save(r"F:\sr2-cn\_E6_before_after.png")
print("写出 _E6_before_after.png  上=修复前 下=修复后")

# 打印每个 slot 的 UV 与墨迹量差异
print("\nslot   U/V(common)   墨迹(官方) 墨迹(汉化)")
for s in CJK:
    print("  %-5d (%4d,%4d)  %-9d %-9d" % (s, U(s), V(s),
        int((cell(ALP_OFF,s)>8).sum()), int((cell(ALP_HAN,s)>8).sum())))
