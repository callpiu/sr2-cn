# -*- coding: utf-8 -*-
"""REC1 完整渲染：所有 41 个 slot（含 ASCII）在修复前/后引擎路径下的渲染"""
import sys, os, struct, hashlib
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BAK  = r"F:\sr2-cn\_backup_E"

vc = Vpp(os.path.join(GAME, "common.vpp_pc"))
ec = vc.find("fnt_chinese", "vf3_pc")
co = vc.data_start + ec['body']
N = struct.unpack_from('<I', vc.data, co + 8)[0]
UOFF = 0xBC + N*16; VOFF = UOFF + N*4
U = lambda i: struct.unpack_from('<H', vc.data, co + UOFF + i*2)[0] if i < N else 0
V = lambda i: struct.unpack_from('<H', vc.data, co + VOFF + i*2)[0] if i < N else 0

off_file = [f for f in os.listdir(BAK) if f.startswith("textures.official_")][0]
vt = Vpp(os.path.join(BAK, off_file))
A_OFF = vt.read(next(x for x in vt.entries() if x['name']=='fnt_chinese'))
vt2 = Vpp(os.path.join(GAME, "textures.vpp_pc"))
A_HAN = vt2.read(next(x for x in vt2.entries() if x['name']=='fnt_chinese'))
_, ALP_OFF = dxt3_decode(A_OFF, 2048, 2048)
_, ALP_HAN = dxt3_decode(A_HAN, 2048, 2048)

REC1 = [403,1868,91,102,111,114,109,97,116,93,91,99,111,108,111,114,58,103,114,101,101,110,93,1067,454,364,91,47,102,111,114,109,97,116,93,2699,2328,403,1868,423,1222]

def cell(alp, s, size=26):
    if s >= N: return np.zeros((size,size),'uint8')
    uu, vv = U(s), V(s)
    if vv+size > 2048 or uu+size > 2048: return np.zeros((size,size),'uint8')
    return alp[vv:vv+size, uu:uu+size]

def strip(alp, slots):
    return np.hstack([np.pad(cell(alp,s), ((2,2),(2,2))) for s in slots])

r1 = strip(ALP_OFF, REC1)
r2 = strip(ALP_HAN, REC1)
S = 27
r1 = np.array(Image.fromarray(r1).resize((len(REC1)*S, S), Image.NEAREST))
r2 = np.array(Image.fromarray(r2).resize((len(REC1)*S, S), Image.NEAREST))
cv = np.zeros((S*2+12, r1.shape[1]), 'uint8')
cv[0:S] = r1
cv[S+12:S+12+S] = r2
Image.fromarray(cv).save(r"F:\sr2-cn\_E7_rec1_full.png")
print("写出 _E7_rec1_full.png（上=修复前 下=修复后，41/41 slot 全渲染）")

print("\n每个 slot 在 common(2838) vf3 中的 UV：")
for s in REC1:
    print("  slot=%-5d U=%-5d V=%-5d  rec=%s" % (s, U(s), V(s), struct.unpack_from('<4H', vc.data, co+0xBC+s*16) if s<N else '-'))
