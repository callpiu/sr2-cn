import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
v = Vpp(os.path.join(G, "patch.vpp_pc"))
A = dxt3_decode(v.read(v.find("fnt_chinese", "g_peg_pc")), 2048, 2048)[1]
MY = np.stack([A[1+31*(j//65):1+31*(j//65)+31, 1+31*(j%65):1+31*(j%65)+31].astype(np.int16)
               for j in range(len(M))])

def ident(cell):
    c = cell.astype(np.int16)
    d = np.abs(MY - c[None]).sum(axis=(1, 2))
    j = int(d.argmin())
    return chr(M[j]) if 32 <= M[j] < 0x110000 else "?"

R = [0x4F60, 0x7684, 0x5F1F, 0x5144, 0x4EEC, 0x9700, 0x8981, 0x4F60, 0x7684, 0x4FDD, 0x62A4]
idx = [M.index(c) for c in R]
TARGET = "\u4efb\u74a8\u5076\u5de7\u4f4d\u96c4\u8861\u4efb\u74a8\u4f2a\u8be5"
print("target:", TARGET)

best = []
for cols in range(48, 84):
    for off in (1, 0):
        for step in (31, 32, 30):
            s = []; ok = True
            for i in idx:
                col = i % cols; row = i // cols
                u = off + step*col; vv = off + step*row
                if vv + 31 > 2048 or u + 31 > 2048:
                    ok = False; break
                s.append(ident(A[vv:vv+31, u:u+31]))
            if not ok:
                continue
            st = "".join(s)
            score = sum(1 for a, b in zip(st, TARGET) if a == b)
            best.append((score, cols, off, step, st))
best.sort(key=lambda x: -x[0])
for b in best[:12]:
    print("score=%2d cols=%-3d off=%d step=%-3d -> %s" % b)
print()
# 也试 index 整体偏移
best2 = []
for d in range(-80, 81):
    s = []
    for i in idx:
        j = i + d
        if j < 0 or j >= len(M):
            s.append("?"); continue
        s.append(chr(M[j]) if 32 <= M[j] < 0x110000 else "?")
    st = "".join(s)
    score = sum(1 for a, b in zip(st, TARGET) if a == b)
    best2.append((score, d, st))
best2.sort(key=lambda x: -x[0])
print("index-shift best:", best2[:5])
