"""FK8: read the subtitle glyphs straight off the screenshot by matching each
segmented glyph against all 2795 atlas cells.
"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from PIL import Image
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
v = Vpp(os.path.join(G, "textures.vpp_pc"))
rgb, alpha = dxt3_decode(v.read(v.find("fnt_chinese")), 2048, 2048)

def norm(a):
    a = a.astype(np.float32)
    m = a > (a.max() * 0.35) if a.max() > 0 else a > 1
    ys, xs = np.where(m)
    if len(ys) == 0:
        return None
    a = a[ys.min():ys.max()+1, xs.min():xs.max()+1]
    im = Image.fromarray((a / max(1e-6, a.max()) * 255).astype(np.uint8)).resize((28, 28), Image.LANCZOS)
    z = np.array(im, np.float32) / 255.0
    z = z - z.mean()
    n = np.sqrt((z*z).sum())
    return z / n if n > 0 else None

# build atlas templates
TMPL = []
for i in range(2795):
    col = i % 65; row = i // 65
    x = 1 + 31*col; y = 1 + 31*row
    TMPL.append(norm(alpha[y:y+31, x:x+31]))
IDX = [i for i, t in enumerate(TMPL) if t is not None]
TMAT = np.stack([TMPL[i].ravel() for i in IDX])

def read_line(path, y0, y1, x0, x1, tag):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    white = (r > 185) & (g > 185) & (b > 185)
    green = (g > 140) & (g > r + 45) & (g > b + 45)
    mask = (white | green)[y0:y1, x0:x1]
    prof = mask.sum(axis=0)
    print("\n%s  band=%dx%d  colprofile nonzero cols=%d" % (tag, mask.shape[0], mask.shape[1], (prof > 0).sum()))
    # segment: group columns separated by >=3 empty columns
    runs = []
    inrun = False
    gap = 0
    for x in range(mask.shape[1]):
        if prof[x] > 0:
            if not inrun:
                inrun = True; s = x
            gap = 0
        else:
            if inrun:
                gap += 1
                if gap >= 3:
                    runs.append((s, x - gap + 1)); inrun = False
    if inrun:
        runs.append((s, mask.shape[1]))
    print("  segments:", len(runs), [ (e-s) for s, e in runs ])
    out = []
    for (s, e) in runs:
        seg = mask[:, s:e]
        t = norm(seg.astype(np.float32) * 255)
        if t is None:
            out.append("?"); continue
        sims = TMAT @ t.ravel()
        k = int(np.argmax(sims))
        best = IDX[k]
        top = np.argsort(-sims)[:3]
        out.append("%s(%.2f)" % (chr(M[best]), sims[k]))
    print("  -> " + " ".join(out))
    # raw char list
    ch = []
    for o in out:
        ch.append(o.split("(")[0])
    print("  -> " + "".join(ch))

read_line(r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg", 690, 762, 770, 1300, "SUB1")
read_line(r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg", 693, 733, 560, 1350, "SUB2")
