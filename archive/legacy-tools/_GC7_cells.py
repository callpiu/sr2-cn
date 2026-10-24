# -*- coding: utf-8 -*-
"""GC7: 逐字切分(按 ~31px 等宽摊开) + 匹配, 输出 位置->格子 映射。"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
IMG = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
T = [int(s) for s in v.read(v.find("charlist_CH", "txt")).decode("utf-8","replace").replace("\r","\n").split("\n") if s.strip().isdigit()]
t = Vpp(os.path.join(G, "textures.vpp_pc"))
rgb, A = dxt3_decode(t.read(t.find("fnt_chinese")), 2048, 2048)
PITCH = 31; COLS = 65

def cell(i):
    r_, c_ = i//COLS, i % COLS
    return A[1+PITCH*r_:1+PITCH*r_+PITCH, 1+PITCH*c_:1+PITCH*c_+PITCH]

def norm(a):
    a = a.astype(np.float32); mx = a.max()
    if mx <= 0: return None
    ys, xs = np.where(a > mx*0.35)
    if len(ys) == 0: return None
    a = a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    if a.shape[0] < 5 or a.shape[1] < 3: return None
    im = Image.fromarray((a/mx*255).astype(np.uint8)).resize((24,24), Image.LANCZOS)
    z = np.array(im, np.float32)/255.0
    z -= z.mean(); n = np.sqrt((z*z).sum())
    return (z/n).ravel() if n > 0 else None

TMP = [norm(cell(i)) for i in range(2795)]
ID = [i for i,x in enumerate(TMP) if x is not None]
TM = np.stack([TMP[i] for i in ID])

def run(path, y0, y1, x0, x1, tag):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(np.int16)
    r, g, b = a[:,:,0], a[:,:,1], a[:,:,2]
    M = (((r>180)&(g>180)&(b>180)) | ((g>130)&(g>r+40)&(g>b+40)))[y0:y1, x0:x1]
    H, W = M.shape
    prof = M.sum(axis=0)
    nz = np.where(prof > 0)[0]
    print("\n=== %s  band=%dx%d  ink x[%d..%d]" % (tag, H, W, nz.min(), nz.max()))
    runs = []; inrun = False; gap = 0
    for x in range(W):
        if prof[x] > 0:
            if not inrun: inrun = True; s = x
            gap = 0
        else:
            if inrun:
                gap += 1
                if gap >= 3: runs.append((s, x-gap+1)); inrun = False
    if inrun: runs.append((s, W))
    # 把宽度 > 40 的段按 ~31px 均分
    units = []
    for (s, e) in runs:
        w = e - s
        k = max(1, int(round(w / 31.0)))
        for j in range(k):
            units.append((s + w*j//k, s + w*(j+1)//k))
    print("   段数=%d  摊开后=%d" % (len(runs), len(units)))
    out = []
    for (s, e) in units:
        z = norm(M[:, s:e].astype(np.float32)*255)
        if z is None: out.append("?"); continue
        S = TM @ z
        k = int(np.argmax(S))
        out.append("%s|%d|%.2f" % (chr(T[ID[k]]), ID[k], S[k]))
    print("   逐字:", " ".join(out))
    print("   字形:", "".join(o.split("|")[0] for o in out))
    print("   格子:", [int(o.split("|")[1]) for o in out])

run(os.path.join(IMG,"clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg"), 685, 768, 745, 1125, "SUB1")
run(os.path.join(IMG,"clipboard-2026-10-15T17-42-28-867Z-329ec487.jpg"), 688, 792, 568, 1395, "SUB3")
