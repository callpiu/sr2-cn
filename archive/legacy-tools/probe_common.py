"""决定性检验：common 图集到底配套哪份字表？

已知：
  - common.vpp_pc 有 fnt_chinese.vf3_pc（2838 字形）
  - common.vpp_pc 没有 charlist 文件
  - 官方 patch.vpp_pc 有 charlist_CH（2838 项）+ fnt_chinese.vf3_pc（68300 字节）
  - 第三方 patch.vpp_pc 有 charlist_CH（2795 项）+ fnt_chinese.vf3_pc（67268 字节）

如果 common 图集配套官方 2838 字表，那么用官方字表的索引去抠 common 图集，
应该抠出官方字表说那个索引是哪个字。

检验方法：取官方字表里一批**特征明显的字**（笔画少、易辨认），
用 common vf3 的 U/V 抠出来，看是否吻合。
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

# ---- 官方 2838 字表 ----
OFF = os.path.join(G, "patch.vpp_pc.official_bak")
if not os.path.exists(OFF):
    OFF = r"F:\sr2-cn\_experiment_A_backup\root\patch.vpp_pc"
vo = Vpp(OFF)
tw = [int(l) for l in vo.read(vo.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("官方 charlist_CH: %d 项" % len(tw))

# ---- 第三方 2795 字表 ----
vc = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in vc.read(vc.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("第三方 charlist_CH: %d 项" % len(cn))

# ---- 三个字体的 vf3 ----
def load_vf3(vpp, name="fnt_chinese"):
    vf3 = bytes(vpp.read(vpp.find(name, "vf3_pc")))
    N = struct.unpack_from("<i", vf3, 0x08)[0]
    U0 = 0xD0 + N * 16
    U = list(struct.unpack_from("<%di" % N, vf3, U0))
    nV = (len(vf3) - (U0 + N * 4)) // 4
    V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
    return N, U, V

Np, Up, Vp = load_vf3(vc)
print("第三方 vf3: N=%d" % Np)
vcm = Vpp(os.path.join(G, "common.vpp_pc"))
Nc, Uc, Vc = load_vf3(vcm)
print("common  vf3: N=%d" % Nc)

# ---- 图集 ----
_, al_p = dxt3_decode(bytes(vc.read(vc.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)
with open(os.path.join(G, "textures.vpp_pc"), "rb") as f:
    f.seek(85407184)
    _, al_c = dxt3_decode(f.read(4194304), 2048, 2048)
print()

# ---- 选一批特征字，检验各组合 ----
# 选官方字表里靠前、笔画少、辨识度高的字
probe = "一二三四五六七八九十日月山川口田人中大小上下左右"
idxs_tw = []
for ch in probe:
    cp = ord(ch)
    idxs_tw.append(tw.index(cp) if cp in tw else -1)
print("探测字: %s" % probe)
print("官方字表索引: %s" % idxs_tw)
print()


def sheet(atlas, pos, path, cw=31, ch=28):
    tiles = []
    for (x, y) in pos:
        g = atlas[y:y + ch, x:x + cw]
        if g.shape != (ch, cw):
            pad = np.zeros((ch, cw), np.uint8)
            pad[:g.shape[0], :g.shape[1]] = g
            g = pad
        tiles.append(g)
        tiles.append(np.full((ch, 2), 255, np.uint8))
    s = np.concatenate(tiles, axis=1)
    Image.fromarray(255 - s).resize((s.shape[1] * 6, s.shape[0] * 6), Image.NEAREST).save(path)


# 组合 1：common 图集 + 官方字表索引 + common vf3 U/V
valid = [(i, Uc[i], Vc[i]) for i in idxs_tw if i >= 0 and i < Nc]
sheet(al_c, [(x, y) for _, x, y in valid], os.path.join(OUT, "P1_common_atlas_twidx_uv.png"))
print("P1) common 图集 + 官方字表索引 + common U/V  -> P1_common_atlas_twidx_uv.png")

# 组合 2：common 图集 + 官方字表索引 + 30x31 网格
def grid(i, ox=2, oy=34, cw=30, ch=31, per=66):
    return (ox + (i % per) * cw, oy + (i // per) * ch)
valid2 = [grid(i) for i in idxs_tw if i >= 0]
sheet(al_c, valid2, os.path.join(OUT, "P2_common_atlas_twidx_grid.png"))
print("P2) common 图集 + 官方字表索引 + 30x31 网格 -> P2_common_atlas_twidx_grid.png")

# 组合 3：第三方图集 + 第三方字表索引（对照组，应该正确）
idx_cn = [cn.index(ord(ch)) if ord(ch) in cn else -1 for ch in probe]
valid3 = [(Up[i], Vp[i]) for i in idx_cn if i >= 0]
sheet(al_p, valid3, os.path.join(OUT, "P3_patch_atlas_cnidx_uv.png"))
print("P3) 第三方图集 + 第三方字表 + U/V（对照组）-> P3_patch_atlas_cnidx_uv.png")

print()
print("期望每个图都显示: %s" % " ".join(probe))
