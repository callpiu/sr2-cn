# -*- coding: utf-8 -*-
"""GC5: 全量滑窗相关 —— 把字幕整行逐像素的最佳图集格子提取出来。"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
IMG = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images"

# ---- charlist (汉化) ----
v = Vpp(os.path.join(G, "patch.vpp_pc"))
T = [int(s) for s in v.read(v.find("charlist_CH", "txt")).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]
print("charlist:", len(T))

# ---- atlas (汉化) ----
t = Vpp(os.path.join(G, "textures.vpp_pc"))
rgb, A = dxt3_decode(t.read(t.find("fnt_chinese")), 2048, 2048)

PITCH = 31; COLS = 65
def cell(i):
    return A[1 + PITCH*(i//COLS): 1 + PITCH*(i//COLS) + PITCH,
             1 + PITCH*(i % COLS): 1 + PITCH*(i % COLS) + PITCH]

def norm(a):
    a = a.astype(np.float32); mx = a.max()
    if mx <= 0: return None
    ys, xs = np.where(a > mx*0.35)
    if len(ys) == 0: return None
    a = a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    im = Image.fromarray((a/mx*255).astype(np.uint8)).resize((24, 24), Image.LANCZOS)
    z = np.array(im, np.float32)/255.0
    z -= z.mean(); n = np.sqrt((z*z).sum())
    return (z/n).ravel() if n > 0 else None

TMP = [norm(cell(i)) for i in range(2795)]
ID = [i for i, x in enumerate(TMP) if x is not None]
TM = np.stack([TMP[i] for i in ID])
print("templates:", TM.shape)

def line_cells(path, tag):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(np.int16)
    r, g, b = a[:,:,0], a[:,:,1], a[:,:,2]
    M = ((r>180)&(g>180)&(b>180)) | ((g>130)&(g>r+40)&(g>b+40))
    ys, xs = np.where(M)
    # 只取最下方那一大团(字幕)
    y0 = ys.max()-45; y1 = ys.max()+3
    sub = M[y0:y1, :]
    colp = sub.sum(axis=0)
    nz = np.where(colp > 0)[0]
    x0, x1 = nz.min()-3, nz.max()+4
    print("\n=== %s  band y[%d,%d) x[%d,%d)  w=%d" % (tag, y0, y1, x0, x1, x1-x0))
    band = sub[:, x0:x1].astype(np.float32)*255
    H, W = band.shape
    # 垂直方向对齐: 用整行的 bbox
    yy = np.where(band.max(axis=1) > 0)[0]
    top, bot = yy.min(), yy.max()+1
    gh = bot-top
    # 把每个 x 处的 31 高窗口取出, 归一化到 24x24
    wins = []
    for x in range(0, W-31, 2):
        w = band[top:top+31, x:x+31]
        if w.shape != (31,31): break
        z = norm(w)
        wins.append(z if z is not None else np.zeros(576, np.float32))
    Wm = np.stack(wins)
    S = TM @ Wm.T                      # (2793, Nx)
    best = np.argmax(S, axis=0)
    sc = S[best, np.arange(S.shape[1])]
    lab = [ID[k] for k in best]
    # 打印: 每 8 像素一行
    out = []
    for i in range(0, len(lab), 4):
        out.append("%d:%s/%.2f" % (i*2, chr(T[lab[i]]), sc[i]))
    print("  ", "  ".join(out))
    return lab, sc

line_cells(os.path.join(IMG, "clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg"), "SUB1")
line_cells(os.path.join(IMG, "clipboard-2026-10-15T17-42-28-867Z-329ec487.jpg"), "SUB3")
