# -*- coding: utf-8 -*-
"""决定性实验 2：common 字体 vs patch 字体的字形图像对比。

理论 H：引擎把 charlist 索引当字形索引，送进 **common 字体**（2838 字形）渲染。
若成立，则 common_glyph[你idx=371] 的图像 == patch_glyph[任idx=336] 的图像。

做法：对 common 的每个候选索引，在全 2795 个 patch 字形里找最佳匹配，
直接「读出」common 那个格子里到底是什么字（不靠截图、不靠假设）。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TEX = os.path.join(G, "textures.vpp_pc")

# ---------------- patch 字体（汉化，2795） ----------------
vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
NP_ = len(CPS)
vf3p = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
UP = np.array(struct.unpack_from("<%di" % NP_, vf3p, 0xAF6C), dtype=np.int64)
VP = np.array(struct.unpack_from("<%di" % NP_, vf3p, 0xDB18), dtype=np.int64)
atlas_p = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
_, ALPHA_P = S.dxt3_decode(bytes(atlas_p), 2048, 2048)
print("[patch] 字表 %d 项" % NP_)


def pglyph(i):
    x, y = int(UP[i]), int(VP[i])
    g = ALPHA_P[y:y + 28, x:x + 31]
    out = np.zeros((28, 31), np.float32)
    h, w = min(28, g.shape[0]), min(31, g.shape[1])
    out[:h, :w] = g[:h, :w]
    return out


# ---------------- common 字体（官方，2838） ----------------
def tex_hdr(path):
    with open(path, "rb") as f:
        d = f.read(5 + 0x14F + 20)
    o = 5 + 0x14F
    num, cs, lo, lf, le = struct.unpack_from("<iiiii", d, o)
    names_at = ((0x800 + lo) & 0xFFFFF800) + 0x800
    ext_at = ((names_at + lf) & 0xFFFFF800) + 0x800
    data_start = ((ext_at + le) & 0xFFFFF800) + 0x800
    return num, data_start, names_at, ext_at


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
        cen = (ds + d, ln)
        print("[textures] fnt_chinese body=%d size=%d" % (ds + d, ln))
        break
assert cen, "textures 里没找到 fnt_chinese"

# common 的 vf3 在 common.vpp_pc
vpc = S.Vpp(os.path.join(G, "common.vpp_pc"))
ec = None
for e in vpc.entries():
    if e["name"].lower() == "fnt_chinese" and e["ext"].lower() == "vf3_pc":
        ec = e
        break
assert ec, "common.vpp_pc 里没找到 fnt_chinese.vf3_pc"
vf3c = bytes(vpc.read(ec))
NC_ = struct.unpack_from("<I", vf3c, 8)[0]
print("[common] vf3 字形数 = %d, 文件长 %d" % (NC_, len(vf3c)))
# 试探 U/V 数组偏移：184 + NC*16 + 4 起
UOFF = 184 + NC_ * 16 + 4
UC = np.array(struct.unpack_from("<%di" % NC_, vf3c, UOFF), dtype=np.int64)
VC = np.array(struct.unpack_from("<%di" % NC_, vf3c, UOFF + NC_ * 4), dtype=np.int64)
print("[common] U 范围 %d~%d  V 范围 %d~%d" % (UC.min(), UC.max(), VC.min(), VC.max()))

with open(TEX, "rb") as f:
    f.seek(cen[0])
    atlas_c = f.read(cen[1])
print("[common] 图集 %d 字节 (期望 4194304)" % len(atlas_c))
_, ALPHA_C = S.dxt3_decode(atlas_c, 2048, 2048)


def cglyph(i):
    x, y = int(UC[i]), int(VC[i])
    g = ALPHA_C[y:y + 28, x:x + 31]
    out = np.zeros((28, 31), np.float32)
    h, w = min(28, g.shape[0]), min(31, g.shape[1])
    out[:h, :w] = g[:h, :w]
    return out


# ---------------- 预计算 patch 全部字形（归一化） ----------------
print("\n预计算 patch %d 个字形..." % NP_)
PG = np.zeros((NP_, 28 * 31), np.float32)
for i in range(NP_):
    g = pglyph(i)
    n = np.linalg.norm(g)
    PG[i] = (g / n).ravel() if n > 0 else g.ravel()

# 找 common 字形在 patch 里的最佳匹配
def best_match(cg):
    n = np.linalg.norm(cg)
    if n == 0:
        return -1, 0.0
    v = (cg / n).ravel()
    sims = PG @ v
    k = int(np.argmax(sims))
    return k, float(sims[k])


IDX = {cp: i for i, cp in enumerate(CPS)}
print("\n索引: 你=%d 任=%d 的=%d 璨=%d 弟=%d 偶=%d 兄=%d 巧=%d 们=%d 位=%d" % (
    IDX[0x4F60], IDX[0x4EFB], IDX[0x7684], IDX[0x74A8], IDX[0x5F1F],
    IDX[0x5076], IDX[0x5144], IDX[0x5DE7], IDX[0x4EEC], IDX[0x4F4D]))

# 已知映射（内存实证的 5 个 + 待验证）
TESTS = [
    (0x193, 0x4EFB, "你->任"), (0x74C, 0x74A8, "的->璨"),
    (0x42B, 0x5076, "弟->偶"), (0x1C6, 0x5DE7, "兄->巧"),
    (0x16C, 0x4F4D, "们->位"),
]
print("\n=== 假设 H：common_glyph[源charlist索引] == 目标字的字形 ===")
for slot, badcp, label in TESTS:
    src_idx = slot - 0x20
    tgt_idx = IDX.get(badcp, -1)
    if src_idx >= NC_ or tgt_idx < 0:
        print("  %-8s 索引越界" % label)
        continue
    cg = cglyph(src_idx)
    k, sim = best_match(cg)
    got = chr(CPS[k]) if 0 <= k < NP_ else "?"
    want = chr(CPS[tgt_idx])
    mark = "✓命中" if k == tgt_idx else "✗"
    print("  %-8s common[%d] 最佳匹配=patch[%d]=%s (ncc=%.3f)  期望=%s  %s"
          % (label, src_idx, k, got, sim, want, mark))

print("\n=== 附加：common 前 60 个字形分别是什么字（直接读出来） ===")
for i in list(range(0, 20)) + [94, 95, 100, 200, 332, 336, 371, 422, 1035, 1784, 1836, 2656, 2837]:
    if i >= NC_:
        continue
    cg = cglyph(i)
    k, sim = best_match(cg)
    got = chr(CPS[k]) if 0 <= k < NP_ else "?"
    print("  common[%4d] -> %s (ncc=%.3f)" % (i, got, sim))
