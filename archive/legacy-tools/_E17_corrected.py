# -*- coding: utf-8 -*-
"""★★★ 修正核心 bug：U/V 数组是 u32（不是 u16）

正确布局：
  文件 = 0xBC 头 + N*16 记录 + N*4 U(u32) + N*4 V(u32)
  验证：patch 2795: 0xBC + 2795*16 + 2795*4 + 2795*4 = 0xBC+44720+11180+11180 = 67268 ✓
  验证：common 2838: 0xBC+45408+11352+11352 = 68300 ✓

用【正确的 u32 读取】重做全部渲染。
"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load(path):
    v = Vpp(path); e = v.find("fnt_chinese", "vf3_pc"); o = v.data_start + e['body']
    N = struct.unpack_from('<I', v.data, o + 8)[0]
    ro = 0xBC; uo = ro + N*16; vo = uo + N*4
    assert vo + N*4 == e['size'], "size mismatch %d vs %d" % (vo+N*4, e['size'])
    R = [struct.unpack_from('<4H', v.data, o+ro+i*16) for i in range(N)]
    U = [struct.unpack_from('<I', v.data, o+uo+i*4)[0] for i in range(N)]
    V = [struct.unpack_from('<I', v.data, o+vo+i*4)[0] for i in range(N)]
    return dict(R=R, U=U, V=V, N=N, size=e['size'])

P = load(os.path.join(G, "patch.vpp_pc"))
C = load(os.path.join(G, "common.vpp_pc"))
print("patch  N=%d size=%d  ✓size自洽" % (P['N'], P['size']))
print("common N=%d size=%d  ✓size自洽" % (C['N'], C['size']))

print("\npatch  U[0:10]=%s V[0:10]=%s" % (P['U'][:10], P['V'][:10]))
print("patch  U[224:232]=%s V[224:232]=%s" % (P['U'][224:232], P['V'][224:232]))
print("common U[0:10]=%s V[0:10]=%s" % (C['U'][:10], C['V'][:10]))
print("common U[224:232]=%s V[224:232]=%s" % (C['U'][224:232], C['V'][224:232]))

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
A_HAN = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
A_TEX = vt.read(next(x for x in vt.entries() if x['name'] == 'fnt_chinese'))
_, PH = dxt3_decode(A_HAN, 2048, 2048)
_, PT = dxt3_decode(A_TEX, 2048, 2048)

CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
c2s = {chr(cp): i + 0x20 for i, cp in enumerate(CL)}

def cell(alp, U, V, s, size=32):
    if s < 0 or s >= len(U): return np.zeros((size,size),'uint8')
    uu, vv = U[s], V[s]
    if uu+size > 2048 or vv+size > 2048: return np.zeros((size,size),'uint8')
    return alp[vv:vv+size, uu:uu+size]

def strip(alp, T, slots, size=32):
    return np.hstack([np.pad(cell(alp,T['U'],T['V'],s,size), ((2,2),(2,2))) for s in slots])

CORRECT = "你的弟兄们需要你的保护"
slots = [c2s[ch] for ch in CORRECT]

tests = [
    ("patch表 + 汉化图集", strip(PH, P, slots)),
    ("patch表 + tex官方图集", strip(PT, P, slots)),
    ("common表 + 汉化图集", strip(PH, C, slots)),
    ("common表 + tex官方图集", strip(PT, C, slots)),
]
W = max(t[1].shape[1] for t in tests); H = sum(t[1].shape[0]+12 for t in tests)+8
cv = np.zeros((H, W+8), 'uint8'); y = 4
for lab, a in tests:
    cv[y:y+a.shape[0], 4:4+a.shape[1]] = a
    y += a.shape[0]+12
Image.fromarray(cv).save(r"F:\sr2-cn\_E17_corrected.png")
print("\n写出 _E17_corrected.png")
for i,(lab,_) in enumerate(tests): print("  行%d: %s" % (i, lab))

# ASCII 自检
ai = strip(PH, P, list(range(26)))
Image.fromarray(np.kron(ai, np.ones((3,3),'uint8'))).save(r"F:\sr2-cn\_E18_patch_ascii.png")
ac = strip(PT, C, list(range(26)))
Image.fromarray(np.kron(ac, np.ones((3,3),'uint8'))).save(r"F:\sr2-cn\_E19_common_ascii.png")
print("写出 _E18( patch表+汉化图集 ASCII) / _E19( common表+tex图集 ASCII)")
