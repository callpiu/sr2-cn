# -*- coding: utf-8 -*-
"""GC1: 决定性实验 —— 从截图逐字匹配图集，求「槽位 -> 图集格子」的真实映射。

SUB1 原文(static_CH) : 你的弟兄们需要你的保护
SUB3 原文(static_CH) : 你的弟兄们正外出做交易，保护他们免受袭击者伤害
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
IMG = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images"

# ---------------------------------------------------------------- charlist
v = Vpp(os.path.join(G, "patch.vpp_pc"))
e = v.find("charlist_CH", "txt")
txt = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
M = [int(s) for s in txt if s.strip().isdigit()]
print("charlist entries:", len(M))

# ---------------------------------------------------------------- atlas
t = Vpp(os.path.join(G, "textures.vpp_pc"))
raw = t.read(t.find("fnt_chinese"))
rgb, alpha = dxt3_decode(raw, 2048, 2048)
print("atlas decoded:", alpha.shape, "alpha max", int(alpha.max()))

PITCH = 31
COLS = 65
def cellimg(i):
    col = i % COLS; row = i // COLS
    x = 1 + PITCH * col; y = 1 + PITCH * row
    return alpha[y:y+PITCH, x:x+PITCH]

def norm(a):
    a = a.astype(np.float32)
    mx = a.max()
    if mx <= 0: return None
    m = a > mx * 0.35
    ys, xs = np.where(m)
    if len(ys) == 0: return None
    a = a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    im = Image.fromarray((a / mx * 255).astype(np.uint8)).resize((28, 28), Image.LANCZOS)
    z = np.array(im, np.float32) / 255.0
    z = z - z.mean()
    n = np.sqrt((z*z).sum())
    return z / n if n > 0 else None

TMPL = [norm(cellimg(i)) for i in range(2795)]
IDX = [i for i, x in enumerate(TMPL) if x is not None]
TMAT = np.stack([TMPL[i].ravel() for i in IDX])
print("templates:", TMAT.shape)

# ---------------------------------------------------------------- segment line
def segments(path, y0, y1, x0, x1):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    white = (r > 180) & (g > 180) & (b > 180)
    green = (g > 130) & (g > r + 40) & (g > b + 40)
    mask = (white | green)[y0:y1, x0:x1]
    prof = mask.sum(axis=0)
    runs = []; inrun = False; gap = 0
    for x in range(mask.shape[1]):
        if prof[x] > 0:
            if not inrun: inrun = True; s = x
            gap = 0
        else:
            if inrun:
                gap += 1
                if gap >= 3:
                    runs.append((s, x - gap + 1)); inrun = False
    if inrun: runs.append((s, mask.shape[1]))
    # merge runs narrower than 6 px into neighbours (broken strokes)
    out = []
    for (s, en) in runs:
        if out and (s - out[-1][1]) <= 1 and (en - s) < 6:
            out[-1] = (out[-1][0], en)
        else:
            out.append((s, en))
    return mask, out

def match_line(path, y0, y1, x0, x1, tag):
    mask, runs = segments(path, y0, y1, x0, x1)
    print("\n===", tag, "segments:", len(runs), [e-s for s, e in runs])
    res = []
    for (s, en) in runs:
        seg = mask[:, s:en]
        tt = norm(seg.astype(np.float32) * 255)
        if tt is None:
            res.append(None); continue
        sims = TMAT @ tt.ravel()
        k = int(np.argmax(sims))
        top = np.argsort(-sims)[:3]
        res.append((IDX[k], float(sims[k]),
                    [(IDX[j], chr(M[IDX[j]]), float(sims[j])) for j in top]))
    for i, r in enumerate(res):
        if r is None:
            print("  %2d  ?" % i); continue
        c, sc, top = r
        print("  %2d  cell=%-5d %s  (%.3f)   top3=%s" % (
            i, c, chr(M[c]), sc, " ".join("%s:%d/%.2f" % (ch, cc, ss) for cc, ch, ss in top)))
    return res

# SUB1  ("你的弟兄们需要你的保护")
r1 = match_line(os.path.join(IMG, "clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg"),
                690, 762, 740, 1120, "SUB1")
# SUB3  ("你的弟兄们正外出做交易，保护他们免受袭击者伤害")
r3 = match_line(os.path.join(IMG, "clipboard-2026-10-15T17-42-28-867Z-329ec487.jpg"),
                690, 790, 570, 1400, "SUB3")

# ---------------------------------------------------------------- decode strings
def dec_str(code_list):
    return "".join(chr(M[c - 32]) for c in code_list)

print("\n--- 若 SUB1 是 '你的弟兄们需要你的保护' 其槽位 ---")
s1 = "你的弟兄们需要你的保护"
for ch in s1:
    u = ord(ch)
    print("   %s U+%04X -> charlist idx %s" % (ch, u, M.index(u) if u in M else "NOT-IN-CL"))
