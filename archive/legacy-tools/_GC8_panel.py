# -*- coding: utf-8 -*-
"""GC8: 对照组 —— HUD 面板(显示正常)的字形在汉化图集里落在哪些格子?
   若落在「正确槽位」-> 面板字体索引正确; 再用它反推字幕的问题。
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
IMG = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
T = [int(s) for s in v.read(v.find("charlist_CH", "txt")).decode("utf-8","replace").replace("\r","\n").split("\n") if s.strip().isdigit()]
IDX = {c: i for i, c in enumerate(T)}

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
    z = np.array(im, np.float32)/255.0; z -= z.mean(); n = np.sqrt((z*z).sum())
    return (z/n).ravel() if n > 0 else None
TMP = [norm(cell(i)) for i in range(2795)]
IDS = [i for i,x in enumerate(TMP) if x is not None]
TM = np.stack([TMP[i] for i in IDS])

def readline(im, y0, y1, x0, x1, tag):
    a = np.array(im.convert("RGB")).astype(np.int16)
    r, g, b = a[:,:,0], a[:,:,1], a[:,:,2]
    M = ((r>170)&(g>170)&(b>170))[y0:y1, x0:x1]
    prof = M.sum(axis=0)
    runs = []; inrun=False; gap=0
    for x in range(M.shape[1]):
        if prof[x] > 0:
            if not inrun: inrun=True; s=x
            gap=0
        else:
            if inrun:
                gap+=1
                if gap>=3: runs.append((s,x-gap+1)); inrun=False
    if inrun: runs.append((s, M.shape[1]))
    print("\n=== %s  runs=%d widths=%s" % (tag, len(runs), [e-s for s,e in runs]))
    out=[]
    for (s,e) in runs:
        z = norm(M[:, s:e].astype(np.float32)*255)
        if z is None: out.append(("?", -1, 0)); continue
        S = TM @ z; k = int(np.argmax(S))
        out.append((chr(T[IDS[k]]), IDS[k], float(S[k])))
    print("   字形:", "".join(o[0] for o in out))
    print("   格子:", [o[1] for o in out])
    print("   分数:", ["%.2f"%o[2] for o in out])
    return out

im = Image.open(os.path.join(IMG,"clipboard-2026-10-15T17-42-28-867Z-329ec487.jpg"))
readline(im, 98, 132, 222, 420, "面板第1行 直升机突击")
readline(im, 138, 172, 222, 420, "面板第2行 已完成停靠")
readline(im, 178, 215, 222, 420, "面板第3行 面包车耐久")

# 找出这些字在字符表里的正确槽位
for s in ("直升机突击","已完成停靠","面包车耐久"):
    print(s, "->", [IDX[ord(c)] for c in s])
