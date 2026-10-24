import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
v = Vpp(os.path.join(G, "patch.vpp_pc"))
b = v.read(v.find("fnt_chinese", "vf3_pc"))
N = struct.unpack_from("<I", b, 8)[0]
recs = [struct.unpack_from("<IIII", b, 0xBC + i*16) for i in range(N)]
uo = 0xBC + N*16
U = [struct.unpack_from("<I", b, uo + i*4)[0] for i in range(N)]
V = [struct.unpack_from("<I", b, uo + N*4 + i*4)[0] for i in range(N)]
A = dxt3_decode(v.read(v.find("fnt_chinese", "g_peg_pc")), 2048, 2048)[1]

SZ = 28

def norm(x):
    x = x.astype(np.float32)
    mx = x.max()
    return x / mx if mx > 0 else x

templates = np.zeros((N, SZ, SZ), np.float32)
for j in range(N):
    w, h = recs[j][0], recs[j][1]
    if w <= 0 or h <= 0:
        continue
    c = A[V[j]:V[j]+h, U[j]:U[j]+w]
    if c.size == 0:
        continue
    templates[j] = norm(np.array(Image.fromarray(c).resize((SZ, SZ), Image.BILINEAR)))
print("templates:", templates.shape, " M len:", len(M))

p = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg"
a = np.array(Image.open(p).convert("RGB")).astype(np.int16)
bright = (a[:, :, 0] > 205) & (a[:, :, 1] > 205) & (a[:, :, 2] > 205)
band = bright[675:775, :]
cols = band.sum(axis=0)
runs = []; inr = False
for x, c in enumerate(cols):
    if c > 0 and not inr:
        inr = True; s = x
    elif c == 0 and inr:
        inr = False; runs.append((s, x))
if inr: runs.append((s, len(cols)))
runs = [(s, e) for s, e in runs if e - s >= 5]
print("runs:", len(runs))

res = []
for (s, e) in runs:
    colm = band[:, s:e]
    nz = np.where(colm.sum(axis=1) > 0)[0]
    if len(nz) == 0:
        continue
    gimg = (colm[nz.min():nz.max()+1, :].astype(np.uint8)) * 255
    q = norm(np.array(Image.fromarray(gimg).resize((SZ, SZ), Image.BILINEAR)))
    d = ((templates - q[None]) ** 2).sum(axis=(1, 2))
    order = np.argsort(d)[:3]
    j = int(order[0])
    ch = chr(M[j]) if 32 <= M[j] < 0x110000 else "?"
    res.append((s, e, j, ch))
    print("  x=%4d..%4d  top3 j=%s  chars=%s  dist=%.1f" % (
        s, e, order.tolist(),
        [chr(M[k]) if 32 <= M[k] < 0x110000 else "?" for k in order], d[j]))
print()
print("MATCHED:", "".join(r[3] for r in res))
print("INDICES:", [r[2] for r in res])
