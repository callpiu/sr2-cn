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
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")

def uv(p, name, ext):
    v = Vpp(p); e = v.find(name, ext)
    b = v.read(e)
    N = struct.unpack_from("<I", b, 8)[0]
    uo = 0xBC + N * 16
    U = [struct.unpack_from("<I", b, uo + i*4)[0] for i in range(N)]
    V = [struct.unpack_from("<I", b, uo + N*4 + i*4)[0] for i in range(N)]
    return U, V

def atl(p, name, ext, w, h):
    v = Vpp(p); e = v.find(name, ext)
    return dxt3_decode(v.read(e), w, h)[1]

myU, myV = uv(os.path.join(G, "patch.vpp_pc"), "fnt_chinese", "vf3_pc")
ofU, ofV = uv(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "fnt_chinese", "vf3_pc")
A_my = atl(os.path.join(G, "patch.vpp_pc"), "fnt_chinese", "g_peg_pc", 2048, 2048)
A_of = atl(r"F:\sr2-cn\vpp_backup\textures.vpp_pc.orig", "fnt_chinese", None, 2048, 2048)

# 我的图集：cell j 位于 (1+31*(j%65), 1+31*(j//65))，内容 = M[j]
def my_cell(j):
    u = 1 + 31 * (j % 65); v = 1 + 31 * (j // 65)
    return A_my[v:v+31, u:u+31].astype(np.int16)

# 预取所有 my 图集格子用于匹配
MYCELLS = np.stack([my_cell(j) for j in range(len(M))])   # (2795,31,31)

def identify(cell):
    c = cell.astype(np.int16)
    d = np.abs(MYCELLS - c[None, :, :]).sum(axis=(1, 2))
    j = int(d.argmin())
    return j, chr(M[j]) if 32 <= M[j] < 0x110000 else "?"

def cell_from(A, u, v):
    if v + 31 > A.shape[0] or u + 31 > A.shape[1]:
        return np.zeros((31, 31), np.uint8)
    return A[v:v+31, u:u+31]

R = [0x4F60, 0x7684, 0x5F1F, 0x5144, 0x4EEC, 0x9700, 0x8981, 0x4F60, 0x7684, 0x4FDD, 0x62A4]
idxM = [M.index(c) for c in R]
idxO = [O.index(c) if c in O else 0 for c in R]

combos = [
    ("mine_atlas+my_uv  @M", A_my, myU, myV, idxM),
    ("mine_atlas+off_uv @M", A_my, ofU, ofV, idxM),
    ("off_atlas +my_uv  @M", A_of, myU, myV, idxM),
    ("off_atlas +off_uv @M", A_of, ofU, ofV, idxM),
    ("mine_atlas+my_uv  @O", A_my, myU, myV, idxO),
    ("off_atlas +my_uv  @O", A_of, myU, myV, idxO),
    ("off_atlas +off_uv @O", A_of, ofU, ofV, idxO),
    ("mine_atlas+off_uv @O", A_my, ofU, ofV, idxO),
]
print("expected garbage on screen: ren can ou qiao wei xiong heng ren can wei gai")
print()
for name, A, U, V, idx in combos:
    out = []
    for i in idx:
        if i >= len(U):
            out.append("?"); continue
        c = cell_from(A, U[i], V[i])
        _, ch = identify(c)
        out.append(ch)
    print("%-24s -> %s" % (name, "".join(out)))
