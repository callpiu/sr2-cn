# -*- coding: utf-8 -*-
"""★ 关键复检：引擎路径 = common.vf3 + textures图集
   现在用【官方原版 textures 图集】+ 不同 vf3 组合，穷举正确渲染。

   注意：当前 texts 图集已被我替换为 patch 版（md5 34034076）。
   先用备份恢复逻辑做离线渲染，找出【真正能渲染出正确中文】的组合。
"""
import sys, os, struct, glob
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 三张图集
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
A_PATCH = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
bakE = sorted(glob.glob(r"F:\sr2-cn\_backup_E\*.vpp_pc"))[0]
ve = Vpp(bakE)
A_OFFICIAL = ve.read(next(x for x in ve.entries() if x['name'] == 'fnt_chinese'))
print("patch 图集   md5", __import__('hashlib').md5(A_PATCH).hexdigest())
print("官方图集      md5", __import__('hashlib').md5(A_OFFICIAL).hexdigest())

# 两张 vf3
def load_vf3(buf_or_path):
    if isinstance(buf_or_path, str):
        v = Vpp(buf_or_path); e = v.find("fnt_chinese", "vf3_pc")
        o = v.data_start + e['body']; d = v.data; base = o; sz = e['size']
    else:
        d, base, sz = buf_or_path, 0, len(buf_or_path)
    N = struct.unpack_from('<I', d, base + 8)[0]
    uo = 0xBC + N*16; vo = uo + N*4
    U = [struct.unpack_from('<I', d, base+uo+i*4)[0] for i in range(N)]
    V = [struct.unpack_from('<I', d, base+vo+i*4)[0] for i in range(N)]
    return U, V, N

# patch vf3（从 patch.vpp_pc 读）
UP, VP, NP = load_vf3(os.path.join(G, "patch.vpp_pc"))
# 官方 common vf3（从备份读）
bakF = sorted(glob.glob(r"F:\sr2-cn\_backup_F\*.vpp_pc"))[0]
UC, VC, NC = load_vf3(bakF)
print("patch  vf3 N=%d   官方 common vf3 N=%d" % (NP, NC))

vp_ = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in vp_.read(vp_.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]
c2i = {}
for i, cp in enumerate(CL):
    c2i.setdefault(chr(cp), i)

_, AH = dxt3_decode(A_PATCH, 2048, 2048)
_, AO = dxt3_decode(A_OFFICIAL, 2048, 2048)

TARGET = "你的弟兄们需要你的保护"
idx = [c2i[c] for c in TARGET]

def row(U, V, A, idxs, size=32):
    out = []
    for s in idxs:
        if 0 <= s < len(U):
            u, vv = U[s], V[s]
            if u+size <= 2048 and vv+size <= 2048:
                out.append(A[vv:vv+size, u:u+size]); continue
        out.append(np.zeros((size, size), 'uint8'))
    return np.hstack([np.pad(x, ((2,2),(2,2))) for x in out])

tests = [
    ("patchvf3 + official图集", row(UP, VP, AO, idx)),
    ("patchvf3 + patch图集",    row(UP, VP, AH, idx)),
    ("commonvf3 + official图集",row(UC, VC, AO, idx)),
    ("commonvf3 + patch图集",   row(UC, VC, AH, idx)),
]
W = max(t[1].shape[1] for t in tests); H = sum(t[1].shape[0]+12 for t in tests)+8
cv = np.zeros((H, W+8), 'uint8'); y = 4
for lab, a in tests:
    cv[y:y+a.shape[0], 4:4+a.shape[1]] = a; y += a.shape[0]+12
Image.fromarray(cv).save(r"F:\sr2-cn\_G1_recheck.png")
print("\n写出 _G1_recheck.png")
for i, (l, _) in enumerate(tests): print("  行%d %s" % (i, l))
