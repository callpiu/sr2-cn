# -*- coding: utf-8 -*-
"""GC4: 用同一批截图字形去匹配三份中文图集, 看哪一份在「正确槽位」上对得上。

正确槽位(来自 static_CH piece#3461 的 code-32):
  [371,1836,1035,422,332,2667,2296,371,1836,391,1190]
"""
import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
IMG = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images"
SLOTS = [371, 1836, 1035, 422, 332, 2667, 2296, 371, 1836, 391, 1190]

def atlas_of(path, name, ext=None):
    v = Vpp(path)
    if ext: e = v.find(name, ext)
    else:
        e = None
        for x in v.entries():
            if x["name"] == name: e = x; break
    return v.read(e)

CANDS = [
    ("汉化(patch/HAN)",  r"F:\sr2-cn\_zip92\黑道圣徒2简体汉化补丁\patch.vpp_pc", "fnt_chinese", "g_peg_pc"),
    ("官方(patch/orig)", r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig",             "fnt_chinese", "g_peg_pc"),
    ("官方(textures)",   r"F:\sr2-cn\_backup_E\textures.official_20261013_174215.vpp_pc", "fnt_chinese", None),
    ("当前(patch)",      os.path.join(G, "patch.vpp_pc"), "fnt_chinese", "g_peg_pc"),
    ("当前(textures)",   os.path.join(G, "textures.vpp_pc"), "fnt_chinese", None),
]

PITCH = 31
def templates(raw, cols):
    rgb, alpha = dxt3_decode(raw, 2048, 2048)
    out = []
    n = cols * (2048 // PITCH)
    for i in range(min(n, 3000)):
        col = i % cols; row = i // cols
        x = 1 + PITCH * col; y = 1 + PITCH * row
        if y + PITCH > 2048: break
        out.append(alpha[y:y+PITCH, x:x+PITCH])
    return out

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
    z -= z.mean()
    nn = np.sqrt((z*z).sum())
    return z / nn if nn > 0 else None

def segs(path, y0, y1, x0, x1):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mask = ((r > 180) & (g > 180) & (b > 180)) | ((g > 130) & (g > r + 40) & (g > b + 40))
    mask = mask[y0:y1, x0:x1]
    prof = mask.sum(axis=0)
    runs = []; inrun = False; gap = 0
    for x in range(mask.shape[1]):
        if prof[x] > 0:
            if not inrun: inrun = True; s = x
            gap = 0
        else:
            if inrun:
                gap += 1
                if gap >= 3: runs.append((s, x - gap + 1)); inrun = False
    if inrun: runs.append((s, mask.shape[1]))
    return mask, runs

mask, runs = segs(os.path.join(IMG, "clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg"), 690, 762, 740, 1120)
print("SUB1 段:", len(runs), [e-s for s, e in runs])
glyphs = []
for (s, e) in runs:
    t = norm(mask[:, s:e].astype(np.float32) * 255)
    glyphs.append(t)

# SUB1 的 11 个位置, 前 3 段是单字, 第 4 段(91px)是 3 个字 -> 手工摊开
# 顺序: 0:你 1:的 2:弟 3:兄 4:们 5:需 6:要 7:你 8:的 9:保 10:护
# 段:   0    1    2    [3=兄们需]  4    5    6    7    8
# 对应: 0    1    2     3,4,5      6    7    8    9    10
mapping = [(0,0),(1,1),(2,2),(4,6),(5,7),(6,8),(7,9),(8,10)]
print("可用的单字段: seg->char_index", mapping)

for tag, path, name, ext in CANDS:
    raw = atlas_of(path, name, ext)
    print("\n=== %-18s %8d md5=%s" % (tag, len(raw), hashlib.md5(raw).hexdigest()[:12]))
    for cols in (65, 66):
        T = templates(raw, cols)
        N = [norm(t) for t in T]
        ID = [i for i, t in enumerate(N) if t is not None]
        MAT = np.stack([N[i].ravel() for i in ID])
        line = []
        for segi, ci in mapping:
            if segi >= len(glyphs) or glyphs[segi] is None: continue
            sims = MAT @ glyphs[segi].ravel()
            k = int(np.argmax(sims))
            cell = ID[k]
            want = SLOTS[ci]
            line.append("pos%d(%s): cell %d %s(%.2f)" % (
                ci, "want%d" % want, cell,
                "OK" if cell == want else "xx", sims[k]))
        print("  cols=%d" % cols)
        for l in line: print("     ", l)
