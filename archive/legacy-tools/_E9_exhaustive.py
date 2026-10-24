# -*- coding: utf-8 -*-
"""穷举 4 张表 x 2 张图集 x 3 种索引，找哪一组能渲染出 '你的弟兄们需要你的保护'"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PRISTINE = r"F:\sr2-cn\_fix_candidates"

def load_vf3(path, name="fnt_chinese", ext="vf3_pc"):
    v = Vpp(path)
    cands = [x for x in v.entries() if x['name'] == name]
    print("   entries named %s in %s:" % (name, os.path.basename(path)), [(x['name'], x['ext'], x['size']) for x in cands])
    e = v.find(name, ext)
    o = v.data_start + e['body']
    N = struct.unpack_from('<I', v.data, o + 8)[0]
    uo = 0xBC + N*16; vo = uo + N*4
    U = [struct.unpack_from('<H', v.data, o+uo+i*2)[0] for i in range(N)]
    V = [struct.unpack_from('<H', v.data, o+vo+i*2)[0] for i in range(N)]
    W = [struct.unpack_from('<4H', v.data, o+0xBC+i*16) for i in range(N)]
    return dict(N=N, U=U, V=V, W=W)

VP = Vpp(os.path.join(GAME, "patch.vpp_pc"))
PATCH_T = load_vf3(os.path.join(GAME, "patch.vpp_pc"))
COMMON_T = load_vf3(os.path.join(GAME, "common.vpp_pc"))

# 官方 patch.vpp_pc 里的 vf3（2788?）—来自 pristine
PRIST = os.path.join(PRISTINE, "..", "_day_2026-10-07")
import glob
pris_paths = glob.glob(os.path.join(PRISTINE, "patch_v42*.vpp_pc")) + glob.glob(os.path.join(PRISTINE,"patch_v51*.vpp_pc"))
print("候选 patch vf3 文件:", [os.path.basename(x) for x in pris_paths][:6])

# 图集
A_HAN = VP.read(VP.find("fnt_chinese", "g_peg_pc"))
vt = Vpp(os.path.join(GAME, "textures.vpp_pc"))
A_TEX = vt.read(next(x for x in vt.entries() if x['name']=='fnt_chinese'))
_, PH = dxt3_decode(A_HAN, 2048, 2048)
_, PT = dxt3_decode(A_TEX, 2048, 2048)

cl = [int(s) for s in VP.read(VP.find("charlist_CH","txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)
TARGET = "你的弟兄们需要你的保护"
slots = [c2s[ch] for ch in TARGET]
print("\n目标 slot:", slots)

def cell(alp, U, V, s, size=30):
    if s < 0 or s >= len(U): return np.zeros((size,size),'uint8')
    uu, vv = U[s], V[s]
    if uu+size > 2048 or vv+size > 2048: return np.zeros((size,size),'uint8')
    return alp[vv:vv+size, uu:uu+size]

def row(alp, T, slots, size=30):
    return np.hstack([np.pad(cell(alp,T['U'],T['V'],s,size), ((2,2),(2,2))) for s in slots])

tests = []
for tn, T in (("common2838", COMMON_T), ("patch2795", PATCH_T)):
    for an, A in (("han图集", PH), ("tex图集", PT)):
        for off, ol in ((0, "slot"), (-0x20, "slot-32")):
            tests.append(("%s | %s | %s" % (tn, an, ol), row(A, T, [s+off for s in slots])))

W = max(t[1].shape[1] for t in tests)
H = sum(t[1].shape[0]+10 for t in tests)+10
cv = np.zeros((H, W+320), 'uint8'); y = 0
for lab, a in tests:
    cv[y:y+a.shape[0], 320:320+a.shape[1]] = a
    y += a.shape[0]+10
Image.fromarray(cv).save(r"F:\sr2-cn\_E9_exhaustive.png")
print("写出 _E9_exhaustive.png  (%d 行)" % len(tests))
for i,(lab,_) in enumerate(tests): print("  行%d y=%d %s" % (i, i*(a.shape[0]+10) if False else 0, lab))
