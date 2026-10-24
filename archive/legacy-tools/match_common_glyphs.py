# -*- coding: utf-8 -*-
"""在官方图集(textures.vpp_pc fnt_chinese, 2838 cell)中定位指定汉字的 cell 索引。

模板取自 patch 图集(汉化字体, 已知 idx->字)，对官方全部 cell 做归一化互相关。
若「乱码5字」的官方 cell 与其汉化 idx 之差为同一常数 k，则 HUD 渲染 = 官方图集 cell[i+k]，
k 即为可计算的修复偏移。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
import numpy as np
from PIL import Image, ImageDraw
import sr2lib as S

sys.stdout.reconfigure(encoding="utf-8")
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# ---- 汉化 charlist & patch 图集 ----
vpp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
CPS = [int(l) for l in vpp.read(vpp.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
NP = len(CPS)
vf3p = bytes(vpp.read(vpp.find("fnt_chinese", "vf3_pc")))
Up = list(struct.unpack_from("<%di" % NP, vf3p, 0xAF6C))
Vp = list(struct.unpack_from("<%di" % NP, vf3p, 0xDB18))
_, Ap = S.dxt3_decode(bytes(vpp.read(vpp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)

# ---- 官方 vf3 & 官方图集 ----
vpc = S.Vpp(os.path.join(G, "common.vpp_pc"))
vf3c = bytes(vpc.read(vpc.find("fnt_chinese", "vf3_pc")))
NC = struct.unpack_from("<I", vf3c, 8)[0]
Uc = list(struct.unpack_from("<%di" % NC, vf3c, 45596))
Vc = list(struct.unpack_from("<%di" % NC, vf3c, 45596 + NC * 4))
with open(os.path.join(G, "textures.vpp_pc"), "rb") as f:
    f.seek(85407184)
    raw = f.read(4194304)
_, Ac = S.dxt3_decode(raw, 2048, 2048)

SZ = 24


def norm(g):
    im = Image.fromarray(g).resize((SZ, SZ), Image.BILINEAR)
    a = np.asarray(im, np.float32) / 255.0
    a -= a.mean()
    n = np.linalg.norm(a)
    return a / n if n > 1e-6 else a


def patch_glyph(i, w=31, h=28):
    g = Ap[Vp[i]:Vp[i] + h, Up[i]:Up[i] + w]
    out = np.zeros((h, w), np.uint8)
    hh, ww = min(h, g.shape[0]), min(w, g.shape[1])
    out[:hh, :ww] = g[:hh, :ww]
    return out


def common_glyph(i, w=30, h=30):
    g = Ac[Vc[i]:Vc[i] + h, Uc[i]:Uc[i] + w]
    out = np.zeros((h, w), np.uint8)
    hh, ww = min(h, g.shape[0]), min(w, g.shape[1])
    out[:hh, :ww] = g[:hh, :ww]
    return out


# 官方图集全部 cell 归一化（先算好，重复用）
print("归一化官方 %d 个 cell ..." % NC)
CB = np.stack([norm(common_glyph(i)) for i in range(NC)]).reshape(NC, -1)

TARGETS = {
    # 字: (汉化idx, 说明)
    "位": (362, "乱码目标 们332->位"),
    "任": (336, "乱码目标 你371->任"),
    "巧": (967, "乱码目标 兄422->巧"),
    "偶": (410, "乱码目标 弟1035->偶"),
    "璨": (1784, "乱码目标 的1836->璨"),
    "你": (371, "想显示的正字"),
    "的": (1836, "想显示的正字"),
    "弟": (1035, "想显示的正字"),
    "兄": (422, "想显示的正字"),
    "们": (332, "想显示的正字"),
}

results = {}
for ch, (hidx, note) in TARGETS.items():
    tpl = norm(patch_glyph(hidx))
    sc = CB @ tpl.reshape(-1)
    top = np.argsort(sc)[::-1][:5]
    results[ch] = [(int(t), float(sc[t])) for t in top]
    print("%s(汉化idx=%d %s): " % (ch, hidx, note) +
          "  ".join("cell%d=%.3f" % (c, s) for c, s in results[ch]))

print()
print("=== 偏移检验（乱码5字：官方cell - 汉化idx 是否为常数）===")
for ch in ("位", "任", "巧", "偶", "璨"):
    hidx = TARGETS[ch][0]
    best = results[ch][0][0]
    print("  %s: 官方cell=%d 汉化idx=%d 差=%d" % (ch, best, hidx, best - hidx))

# 输出可视化核对图
OUT = r"F:/sr2-cn/_字体核对"
os.makedirs(OUT, exist_ok=True)
img = Image.new("L", (10 * 150, 3 * 140), 0)
d = ImageDraw.Draw(img)
for k, ch in enumerate(list(TARGETS.keys())[:10]):
    hidx = TARGETS[ch][0]
    r, c = divmod(k, 5)
    px, py = c * 150 * 2 + (0 if c < 5 else 0), 0,  # noqa
for k, ch in enumerate(TARGETS.keys()):
    hidx = TARGETS[ch][0]
    r, c = divmod(k, 5)
    px, py = (k % 5) * 300, (k // 5) * 280
    t = Image.fromarray(patch_glyph(hidx)).resize((120, 108), Image.NEAREST)
    img.paste(t, (px, py + 24))
    d.text((px + 2, py + 4), "%s patch%d" % (ch, hidx), fill=220)
    best = results[ch][0][0]
    g2 = Image.fromarray(common_glyph(best)).resize((120, 120), Image.NEAREST)
    img.paste(g2, (px + 150, py + 24))
    d.text((px + 152, py + 4), "官方cell%d" % best, fill=220)
p = os.path.join(OUT, "34_匹配核对.png")
img.save(p)
print("  ->", p)
