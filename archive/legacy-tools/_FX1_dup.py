"""FX1: locate every occurrence of a glyph inside the installed atlas.
template = cell(M.index(ch)) using the 65-col formula, then scan all cells.
"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")

v = Vpp(os.path.join(G, "textures.vpp_pc"))
raw = v.read(v.find("fnt_chinese"))
rgb, alpha = dxt3_decode(raw, 2048, 2048)
A = alpha.astype(np.float32)

def cell(idx, cols=65, off=1, step=31, size=31):
    col = idx % cols; row = idx // cols
    x = off + step * col; y = off + step * row
    return A[y:y+size, x:x+size]

def scan(tmpl, cols=65, off=1, step=31, size=31, thr=0.90):
    n = 2795
    hits = []
    t = tmpl - tmpl.mean()
    tn = np.sqrt((t*t).sum())
    for i in range(n):
        c = cell(i, cols, off, step, size)
        cc = c - c.mean()
        d = np.sqrt((cc*cc).sum())
        if d < 1e-6:
            continue
        r = float((t*cc).sum() / (tn*d))
        if r >= thr:
            hits.append((round(r, 3), i))
    hits.sort(reverse=True)
    return hits

for ch in [0x4F60, 0x4EFB, 0x7684, 0x74A8]:
    idx = M.index(ch)
    tmpl = cell(idx)
    h = scan(tmpl)
    print("U+%04X  M.idx=%d   -> %d hit(s)" % (ch, idx, len(h)))
    for r, i in h[:8]:
        print("      cell %-6d  r=%.3f   M[cell]=U+%04X" % (i, r, M[i] if i < len(M) else -1))
    print()

# how many cells are blank?
blank = 0
for i in range(2795):
    if cell(i).max() < 20:
        blank += 1
print("blank cells (65col scan):", blank)
