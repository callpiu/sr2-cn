"""验证：common 字体（2838 字形）下，活动串能否正确渲染？

假设
    patch 图集比 charlist 超前 5 位 -> HUD 用 patch 图集时错位
    但 HUD 也许用的是 common 图集（2838 字形，另一套顺序）

做法
    用 common 的 vf3 U/V，按「索引 = 槽位-0x20」抠出活动串的字形。
    如果 common 图集是正确的（与 charlist 对齐），抠出来应显示
    「弟兄们需要你的保护」。
"""
import os, sys, struct
import numpy as np
from PIL import Image

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"

# common 的 vf3
vc = Vpp(os.path.join(G, "common.vpp_pc"))
vf3c = bytes(vc.read(vc.find("fnt_chinese", "vf3_pc")))
Nc = struct.unpack_from("<i", vf3c, 0x08)[0]
U0c = 0xD0 + Nc * 16
Uc = list(struct.unpack_from("<%di" % Nc, vf3c, U0c))
nVc = (len(vf3c) - (U0c + Nc * 4)) // 4
Vc = list(struct.unpack_from("<%di" % nVc, vf3c, U0c + Nc * 4)) + [0] * (Nc - nVc)
print("common vf3: N=%d" % Nc)

# common 的图集（textures.vpp_pc 内）
with open(os.path.join(G, "textures.vpp_pc"), "rb") as f:
    f.seek(85407184)
    _, al_c = dxt3_decode(f.read(4194304), 2048, 2048)

# charlist + 活动槽位
cn = [int(l) for l in vc.read(vc.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
slots = [1067, 454, 364, 2699, 2328, 403, 1868, 423, 1222]
print("字表读出: %s" % "".join(S[x] for x in slots))
print()

# patch 图集作对照
vp = Vpp(os.path.join(G, "patch.vpp_pc.v531_before_mirror.bak"))
_, al_p = dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)
vf3p = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
Np = struct.unpack_from("<i", vf3p, 0x08)[0]
U0p = 0xD0 + Np * 16
Up = list(struct.unpack_from("<%di" % Np, vf3p, U0p))
nVp = (len(vf3p) - (U0p + Np * 4)) // 4
Vp = list(struct.unpack_from("<%di" % nVp, vf3p, U0p + Np * 4)) + [0] * (Np - nVp)


def render(atlas, U, V, N, K, path):
    tiles = []
    for x in slots:
        i = x - 0x20 + K
        if not (0 <= i < N):
            return False
        g = atlas[V[i]:V[i] + 28, U[i]:U[i] + 31]
        if g.shape != (28, 31):
            pad = np.zeros((28, 31), np.uint8)
            pad[:g.shape[0], :g.shape[1]] = g
            g = pad
        tiles.append(g)
        tiles.append(np.full((28, 2), 255, np.uint8))
    s = np.concatenate(tiles, axis=1)
    Image.fromarray(255 - s).resize((s.shape[1] * 8, s.shape[0] * 8), Image.NEAREST).save(path)
    return True


for K in (0, -5, 5):
    ok = render(al_c, Uc, Vc, Nc, K, os.path.join(OUT, "common_K%d.png" % K))
    print("common 图集 偏移 %+3d -> common_K%d.png  %s" % (K, K, "OK" if ok else "越界"))
print()
for K in (0, 5, -5):
    ok = render(al_p, Up, Vp, Np, K, os.path.join(OUT, "patch_K%d.png" % K))
    print("patch  图集 偏移 %+3d -> patch_K%d.png   %s" % (K, K, "OK" if ok else "越界"))
print()
print("期望: 弟兄们需要你的保护")
