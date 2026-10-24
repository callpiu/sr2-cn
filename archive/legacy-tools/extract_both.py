"""从两个中文字体图集里抠出指定索引的字形，做对比。

交接文档 §4.2 说：
  - patch 图集：列距 31px
  - common 图集：列距 30px、行距 ≈31px，origin 约 (x=2, y=34)，每行 66 个

本次两种切法都试，看哪个能对上用户报告的乱码。
"""
import os, sys, struct
import numpy as np
from PIL import Image

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_juice_fix"
os.makedirs(OUT, exist_ok=True)

IDX = [1035, 422, 332, 2667, 2296, 371, 1836, 391, 1190]
LABEL = "弟 兄 们 需 要 你 的 保 护"

# ---------- patch 图集 ----------
v = Vpp(os.path.join(G, "patch.vpp_pc"))
_, al_p = dxt3_decode(bytes(v.read(v.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)
vf3p = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
Np = struct.unpack_from("<i", vf3p, 0x08)[0]
U0 = 0xD0 + Np * 16
Up = list(struct.unpack_from("<%di" % Np, vf3p, U0))
nV = (len(vf3p) - (U0 + Np * 4)) // 4
Vp = list(struct.unpack_from("<%di" % nV, vf3p, U0 + Np * 4)) + [0] * (Np - nV)
print("patch  vf3: N=%d, %d 字节" % (Np, len(vf3p)))

# ---------- common 图集（从 textures.vpp_pc 轻量读）----------
vc = Vpp(os.path.join(G, "common.vpp_pc"))
vf3c = bytes(vc.read(vc.find("fnt_chinese", "vf3_pc")))
Nc = struct.unpack_from("<i", vf3c, 0x08)[0]
U0c = 0xD0 + Nc * 16
Uc = list(struct.unpack_from("<%di" % Nc, vf3c, U0c))
nVc = (len(vf3c) - (U0c + Nc * 4)) // 4
Vc = list(struct.unpack_from("<%di" % nVc, vf3c, U0c + Nc * 4)) + [0] * (Nc - nVc)
print("common vf3: N=%d, %d 字节" % (Nc, len(vf3c)))

TP = os.path.join(G, "textures.vpp_pc")
BODY_OFF = 85407184
with open(TP, "rb") as f:
    f.seek(BODY_OFF)
    data = f.read(4194304)
_, al_c = dxt3_decode(data, 2048, 2048)
print("common 图集: 从 textures.vpp_pc @0x%X 读 %d 字节" % (BODY_OFF, len(data)))
print()


def sheet(atlas, positions, path, cell_w=31, cell_h=28, sep=2):
    tiles = []
    for (x, y) in positions:
        g = atlas[y:y + cell_h, x:x + cell_w]
        if g.shape != (cell_h, cell_w):
            pad = np.zeros((cell_h, cell_w), np.uint8)
            pad[:g.shape[0], :g.shape[1]] = g
            g = pad
        tiles.append(g)
        tiles.append(np.full((cell_h, sep), 255, np.uint8))
    s = np.concatenate(tiles, axis=1)
    Image.fromarray(255 - s).resize((s.shape[1] * 7, s.shape[0] * 7), Image.NEAREST).save(path)
    return s.shape


# A) patch，用 vf3 的 U/V
posA = [(Up[i], Vp[i]) for i in IDX]
sheet(al_p, posA, os.path.join(OUT, "A_patch_uv.png"))
print("A) patch + vf3 U/V      -> A_patch_uv.png")
print("   位置: %s" % posA)

# B) common，用 vf3 的 U/V
posB = [(Uc[i], Vc[i]) for i in IDX]
sheet(al_c, posB, os.path.join(OUT, "B_common_uv.png"))
print("B) common + vf3 U/V     -> B_common_uv.png")
print("   位置: %s" % posB)

# C) common，用 30x31 网格，origin (2,34)，每行 66
def grid_pos(i, ox=2, oy=34, cw=30, ch=31, percol=66):
    r = i // percol
    c = i % percol
    return (ox + c * cw, oy + r * ch)

posC = [grid_pos(i) for i in IDX]
sheet(al_c, posC, os.path.join(OUT, "C_common_grid.png"))
print("C) common + 30x31 网格  -> C_common_grid.png")
print("   位置: %s" % posC)

# D) common，用 31x31 网格，origin (1,1)
posD = [grid_pos(i, 1, 1, 31, 31, 66) for i in IDX]
sheet(al_c, posD, os.path.join(OUT, "D_common_grid31.png"))
print("D) common + 31x31 网格  -> D_common_grid31.png")
print("   位置: %s" % posD)

print()
print("索引:  %s" % IDX)
print("期望:  %s" % LABEL)
print("用户看到: 任 璨 偶 巧 位 雄 衡 伪 该")
