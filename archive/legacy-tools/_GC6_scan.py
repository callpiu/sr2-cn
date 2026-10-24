# -*- coding: utf-8 -*-
"""GC6: 固定字幕带, 滑窗相关, 输出整行「最佳格子」序列。"""
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
    if a.shape[0] < 4 or a.shape[1] < 3: return None
    im = Image.fromarray((a/mx*255).astype(np.uint8)).resize((24,24), Image.LANCZOS)
    z = np.array(im, np.float32)/255.0
    z -= z.mean(); n = np.sqrt((z*z).sum())
    return (z/n).ravel() if n > 0 else None

TMP = [norm(cell(i)) for i in range(2795)]
ID = [i for i,x in enumerate(TMP) if x is not None]
TM = np.stack([TMP[i] for i in ID])
print("templates", TM.shape)

def run(path, y0, y1, x0, x1, tag):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(np.int16)
    r, g, b = a[:,:,0], a[:,:,1], a[:,:,2]
    M = (((r>180)&(g>180)&(b>180)) | ((g>130)&(g>r+40)&(g>b+40)))[y0:y1, x0:x1]
    H, W = M.shape
    print("\n=== %s band %dx%d" % (tag, H, W))
    wins, xs = [], []
    for x in range(0, W-30, 2):
        z = norm(M[:, x:x+30].astype(np.float32)*255)
        if z is None: continue
        wins.append(z); xs.append(x)
    Wm = np.stack(wins)
    S = TM @ Wm.T
    best = np.argmax(S, axis=0); sc = S[best, np.arange(S.shape[1])]
    lab = [ID[k] for k in best]
    # 归并: 连续相同标签 -> 一段
    print("   x  ->  cell  char  score")
    prev = None
    for i in range(len(lab)):
        if lab[i] != prev or sc[i] > 0.55:
            print("   %4d  cell=%-5d %s  %.2f" % (xs[i], lab[i], chr(T[lab[i]]), sc[i]))
            prev = lab[i]

run(os.path.join(IMG,"clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg"), 690, 765, 740, 1130, "SUB1")
run(os.path.join(IMG,"clipboard-2026-10-15T17-42-28-867Z-329ec487.jpg"), 690, 795, 565, 1400, "SUB3")
