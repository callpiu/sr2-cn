# -*- coding: utf-8 -*-
"""最终验收：完全用【游戏目录当前部署的文件】渲染目标字幕

模拟引擎实际加载：
  charlist  <- patch.vpp_pc
  vf3       <- common.vpp_pc（也检查 patch.vpp_pc 是否一致）
  atlas     <- textures.vpp_pc（引擎实际用的那个）
"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
RO = 0xBC


def load_vf3(path):
    v = Vpp(path); b = v.read(v.find("fnt_chinese", "vf3_pc")); del v
    N = struct.unpack_from('<I', b, 8)[0]
    uo = RO + N * 16; vo = uo + N * 4
    return dict(N=N,
                U=[struct.unpack_from('<I', b, uo + i * 4)[0] for i in range(N)],
                V=[struct.unpack_from('<I', b, vo + i * 4)[0] for i in range(N)])


def load_atlas(path):
    v = Vpp(path)
    e = next(x for x in v.entries() if x['name'] == 'fnt_chinese')
    b = v.read(e); del v
    return dxt3_decode(b, 2048, 2048)[1]


print("=" * 60)
print(" 最终验收（用游戏目录当前文件）")
print("=" * 60)

# charlist
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).replace(b"\r\n", b"\n").split(b"\n") if s.strip().isdigit()]
del vp
print("charlist_CH 项数 = %d" % len(CL))

VF_C = load_vf3(os.path.join(G, "common.vpp_pc"))
VF_P = load_vf3(os.path.join(G, "patch.vpp_pc"))
print("common.vf3 N=%d   patch.vf3 N=%d   U/V 相同=%s"
      % (VF_C['N'], VF_P['N'], VF_C['U'] == VF_P['U'] and VF_C['V'] == VF_P['V']))

A = load_atlas(os.path.join(G, "textures.vpp_pc"))
print("textures 图集 = %s" % (A.shape,))

c2i = {chr(cp): i for i, cp in enumerate(CL)}
TEXTS = ["你的弟兄们需要你的保护",
         "保护他们免遭袭击",
         "帮你的兄弟们赶到他们的目的地。"]
SZ = 32


def strip(T, s):
    cells = []
    for ch in s:
        j = c2i.get(ch)
        if j is None:
            cells.append(np.zeros((SZ, SZ), 'uint8')); continue
        uu, vv = T['U'][j], T['V'][j]
        if uu + SZ > 2048 or vv + SZ > 2048:
            cells.append(np.zeros((SZ, SZ), 'uint8')); continue
        cells.append(np.pad(A[vv:vv + SZ, uu:uu + SZ], ((3, 3), (3, 3))))
    return np.hstack(cells)


rows = [strip(VF_C, t) for t in TEXTS]
W = max(r.shape[1] for r in rows)
H = sum(r.shape[0] + 14 for r in rows) + 10
cv = np.zeros((H, W + 12), 'uint8')
y = 6
for r in rows:
    cv[y:y + r.shape[0], 6:6 + r.shape[1]] = r
    y += r.shape[0] + 14
img = Image.fromarray(cv)
img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
out = r"F:\sr2-cn\_FINAL_VERIFY.png"
img.save(out)
print()
print("写出 %s" % out)
for i, t in enumerate(TEXTS):
    print("   行%d 期望: %s" % (i, t))
