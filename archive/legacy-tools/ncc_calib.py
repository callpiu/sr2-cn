# -*- coding: utf-8 -*-
"""NCC 基线校准 + 可视化图样（直接看，不靠猜）"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from PIL import Image, ImageDraw
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TEX = os.path.join(G, "textures.vpp_pc")
OUT = r"F:/sr2-cn/_字体核对"

vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
NP_ = len(CPS)
vf3p = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
UP = np.array(struct.unpack_from("<%di" % NP_, vf3p, 0xAF6C), dtype=np.int64)
VP = np.array(struct.unpack_from("<%di" % NP_, vf3p, 0xDB18), dtype=np.int64)
_, AP = S.dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)


def pglyph(i):
    x, y = int(UP[i]), int(VP[i])
    g = AP[y:y + 28, x:x + 31]
    o = np.zeros((28, 31), np.float32)
    h, w = min(28, g.shape[0]), min(31, g.shape[1])
    o[:h, :w] = g[:h, :w]
    return o


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


def cglyph(i):
    x, y = int(UC[i]), int(VC[i])
    g = AC[y:y + 28, x:x + 31]
    o = np.zeros((28, 31), np.float32)
    h, w = min(28, g.shape[0]), min(31, g.shape[1])
    o[:h, :w] = g[:h, :w]
    return o


# ---------- NCC 基线校准 ----------
print("=== NCC 基线校准（patch 内部）===")
PG = np.zeros((NP_, 28 * 31), np.float32)
for i in range(NP_):
    g = pglyph(i); n = np.linalg.norm(g)
    PG[i] = (g / n).ravel() if n > 0 else g.ravel()


def ncc(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float((a.ravel() @ b.ravel()) / (na * nb))


pairs = [(371, 336, "你vs任"), (371, 362, "你vs位"), (332, 362, "们vs位"),
         (336, 418, "任vs僵"), (1836, 1784, "的vs璨"), (1035, 410, "弟vs偶"),
         (336, 337, "任vs邻"), (371, 372, "你vs邻")]
for i, j, lb in pairs:
    print("  %-10s ncc=%.3f" % (lb, ncc(pglyph(i), pglyph(j))))

# 全表随机对的 NCC 分布
rng = np.random.default_rng(7)
idxs = rng.integers(94, NP_, 4000)
sims = []
GM = PG[94:]
for k in range(0, 4000, 500):
    blk = PG[idxs[k:k + 500]]
    M = blk @ GM.T
    for r in range(M.shape[0]):
        row = M[r].copy()
        row[idxs[k + r] - 94] = -9
        sims.append(float(row.max()))
sims = np.array(sims)
print("\n  随机汉字对的最大 NCC: mean=%.3f  p50=%.3f  p90=%.3f  p99=%.3f  max=%.3f"
      % (sims.mean(), np.percentile(sims, 50), np.percentile(sims, 90),
         np.percentile(sims, 99), sims.max()))
print("  => 阈值参考：NCC>0.90 才算真匹配；0.7~0.8 只是「同为某偏旁」的噪声")


# ---------- 可视化：patch 与 common 同索引并排 ----------
def sheet(fn, rows, mode, cols=10, cell=34):
    """rows: list of (idx, label)"""
    W, H = cols * cell, len(rows) * cell
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    for k, (i, lb) in enumerate(rows):
        r, c = divmod(k, cols)
        g = pglyph(i) if mode == "p" else cglyph(i)
        im = Image.fromarray(g.astype(np.uint8)).resize((cell - 4, cell - 4), Image.NEAREST)
        img.paste(im, (c * cell + 2, r * cell + 2))
        d.text((c * cell + 2, r * cell + cell - 12), lb, fill=180)
    p = os.path.join(OUT, fn)
    img.save(p)
    print("  saved", p)


print("\n=== 渲染可视化图样 ===")
sheet("60_patch_idx325-375.png", [(i, "%d:%s" % (i, chr(CPS[i]))) for i in range(325, 376)], "p")
sheet("61_common_idx325-375.png", [(i, "%d" % i) for i in range(325, 376)], "c")
sheet("62_patch_idx0-60.png", [(i, "%d:%s" % (i, chr(CPS[i]) if 32 <= CPS[i] < 127 else ".")) for i in range(0, 61)], "p")
sheet("63_common_idx0-60.png", [(i, "%d" % i) for i in range(0, 61)], "c")
print("\n关键索引对照:")
for cp, ch in [(0x4F60, "你"), (0x4EFB, "任"), (0x4F4D, "位"), (0x4EEC, "们")]:
    print("  %s U+%04X -> patch idx %d" % (ch, cp, CPS.index(cp)))
