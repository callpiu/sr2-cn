# -*- coding: utf-8 -*-
"""决定性实验 3：直接读出 common 字体每个索引对应的「汉字」。

不再用 NCC 猜（汉字 NCC 噪声 0.8+），改用「索引->码点」的唯一确定性来源：
    patch 图集 idx -> charlist_CH[idx] 是汉化组自洽的（idx==charlist idx）
    common 图集 idx -> ?  需要确定

策略：既然 common[332] 看上去就是「位」= U+4F4D，而内存实证 们(0x16C)->位(U+4F4D)，
说明 common 的字形排列与 charlist_CH 不同。那么：
    对每个已知锚点 (slot, 目标码点)，检查 common[slot] 的 UV 是否落在
    「patch 图集中 目标码点 所在 cell」上 —— 即两个字体的图集是否同一批字形、
    只是排列不同。用 UV 网格公式直接算，零歧义。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TEX = os.path.join(G, "textures.vpp_pc")

vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
NP_ = len(CPS)
vf3p = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
UP = np.array(struct.unpack_from("<%di" % NP_, vf3p, 0xAF6C), dtype=np.int64)
VP = np.array(struct.unpack_from("<%di" % NP_, vf3p, 0xDB18), dtype=np.int64)
_, AP = S.dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)


def tex_hdr(path):
    with open(path, "rb") as f:
        d = f.read(5 + 0x14F + 20)
    o = 5 + 0x14F
    num, cs, lo, lf, le = struct.unpack_from("<iiiii", d, o)
    names_at = ((0x800 + lo) & 0xFFFFF800) + 0x800
    ext_at = ((names_at + lf) & 0xFFFFF800) + 0x800
    return num, ((ext_at + le) & 0xFFFFF800) + 0x800, names_at, ext_at


num, ds, names_at, ext_at = tex_hdr(TEX)
with open(TEX, "rb") as f:
    f.seek(0x800); etab = f.read(num * 28)
    f.seek(names_at); names = f.read(60000)
    f.seek(ext_at); exts = f.read(20000)


def gs(b, o):
    e = b.find(b"\x00", o)
    return b[o:e].decode("ascii", "replace")


cen = None
for i in range(num):
    a, b, c, d, ln, m1, z = struct.unpack_from("<IIiiiii", etab, i * 28)
    if gs(names, a) == "fnt_chinese":
        cen = (ds + d, ln); break

vpc = S.Vpp(os.path.join(G, "common.vpp_pc"))
ec = None
for e in vpc.entries():
    if e["name"].lower() == "fnt_chinese" and e["ext"].lower() == "vf3_pc":
        ec = e; break
vf3c = bytes(vpc.read(ec))
NC_ = struct.unpack_from("<I", vf3c, 8)[0]
UOFF = 184 + NC_ * 16 + 4
UC = np.array(struct.unpack_from("<%di" % NC_, vf3c, UOFF), dtype=np.int64)
VC = np.array(struct.unpack_from("<%di" % NC_, vf3c, UOFF + NC_ * 4), dtype=np.int64)
with open(TEX, "rb") as f:
    f.seek(cen[0]); atlas_c = f.read(cen[1])
_, AC = S.dxt3_decode(atlas_c, 2048, 2048)
print("[common] %d 字形, 图集 %d 字节" % (NC_, len(atlas_c)))

# 逐个比较：common[i] 与 patch[j] 的像素差（用精确像素，非 NCC）
def pix(img, U, V, i):
    x, y = int(U[i]), int(V[i])
    g = img[y:y + 28, x:x + 31]
    o = np.zeros((28, 31), np.float32)
    h, w = min(28, g.shape[0]), min(31, g.shape[1])
    o[:h, :w] = g[:h, :w]
    return o


def score(a, b):
    """同一字形的判据：Alpha 通道逐像素 L1 距离（归一化）"""
    d = np.abs(a - b).sum()
    return d / (28 * 31 * 255.0)


ANCH = [
    (0x193, 0x4EFB, "你->任"), (0x74C, 0x74A8, "的->璨"),
    (0x42B, 0x5076, "弟->偶"), (0x1C6, 0x5DE7, "兄->巧"),
    (0x16C, 0x4F4D, "们->位"),
]
IDX = {cp: i for i, cp in enumerate(CPS)}
print("\n=== 假设 H2：common 图集 slot 索引 -> 目标码点的字形 ===")
print("（common[slot] 的像素 vs patch[目标码点idx] 的像素，L1 距离越小越像）\n")
for slot, badcp, label in ANCH:
    tgt = IDX.get(badcp, -1)
    if slot >= NC_ or tgt < 0:
        print("  %-8s 越界" % label); continue
    a = pix(AC, UC, VC, slot)
    b = pix(AP, UP, VP, tgt)
    # 也跟「源字自己」比，作对照
    src = slot - 0x20
    c = pix(AP, UP, VP, src)
    print("  %-8s common[%d] vs patch[%s]=%s : L1=%.4f   |  对照 common[%d] vs patch[%s]=%s(源) : L1=%.4f"
          % (label, slot, tgt, chr(CPS[tgt]), score(a, b), slot, src, chr(CPS[src]), score(a, c)))

# 反向：common[slot] 到底像 patch 里的哪个字？用 L1 距离全表搜（比 NCC 可靠）
print("\n=== common[slot] 在全 patch 表里按 L1 距离找最佳（前5）===")
PG = np.stack([pix(AP, UP, VP, i) for i in range(NP_)]).reshape(NP_, -1)
for slot, badcp, label in ANCH:
    a = pix(AC, UC, VC, slot).ravel()
    d = np.abs(PG - a).sum(axis=1) / (28 * 31 * 255.0)
    order = np.argsort(d)[:5]
    print("  %-8s common[%d] -> " % (label, slot) +
          "  ".join("%s(%.4f)" % (chr(CPS[k]), d[k]) for k in order))
