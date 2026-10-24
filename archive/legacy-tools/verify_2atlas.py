# -*- coding: utf-8 -*-
"""决定性: 用 textures.vpp_pc 的原厂图集 + patch 的 vf3 UV, 渲染9字"""
import os, sys, struct, re
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

# 两套图集
vp_patch = Vpp(os.path.join(G, "patch.vpp_pc"))
_, atlas_patch = dxt3_decode(bytes(vp_patch.read(vp_patch.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)
vp_tex = Vpp(os.path.join(G, "textures.vpp_pc"))
_, atlas_tex = dxt3_decode(bytes(vp_tex.read(vp_tex.find("fnt_chinese"))), 2048, 2048)

# patch 的 vf3 UV
vf3 = bytes(vp_patch.read(vp_patch.find("fnt_chinese", "vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N * 16
U = list(struct.unpack_from("<%di" % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)

buf = vp_patch.read(vp_patch.find("charlist_CH", "txt"))
end = buf.find(b'//ENDOFFILE')
tbl = [int(x) for x in re.findall(rb'\d+', buf[:end])]
ps = "".join(chr(c) for c in tbl)


def tile(atlas, i):
    x, y = U[i], V[i]
    g = atlas[y:y + 30, x:x + 31]
    if g.shape != (30, 31):
        p = np.zeros((30, 31), np.uint8); p[:g.shape[0], :g.shape[1]] = g; g = p
    return g


targ = "你的弟兄们需要保护"
garb = "任璨偶巧位雄衡伪该"

# 渲染: 用 patch 表 idx -> patch UV -> 取图集格
rows = []
labels = []
for atl, name in [(atlas_patch, "patch集"), (atlas_tex, "tex原厂集")]:
    ts = []
    for c in targ:
        i = ps.find(c)
        ts.append(tile(atl, i)); ts.append(np.full((30, 2), 255, np.uint8))
    rows.append(np.concatenate(ts, axis=1))

s = np.concatenate([np.concatenate([r, np.full((30, 20), 0, np.uint8)], axis=1) for r in rows], axis=0)
Image.fromarray(255 - s).resize((s.shape[1] * 6, s.shape[0] * 6), Image.NEAREST).save(r"F:/sr2-cn/_verify_2atlas.png")
print("上=patch集 下=textures原厂集; 列=你的弟兄们需要保护")
print("写出 _verify_2atlas.png")
