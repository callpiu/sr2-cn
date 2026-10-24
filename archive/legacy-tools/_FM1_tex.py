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

print("=== fnt_chinese entries per VPP ===")
for tag, p in (("game/textures", os.path.join(G, "textures.vpp_pc")),
               ("orig/textures", r"F:\sr2-cn\vpp_backup\textures.vpp_pc.orig"),
               ("game/patch", os.path.join(G, "patch.vpp_pc")),
               ("orig/patch", r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")):
    try:
        v = Vpp(p)
        hits = [(e["name"], e.get("ext"), e["size"]) for e in v.entries() if e["name"] == "fnt_chinese"]
        print("  %-14s -> %s" % (tag, hits))
    except Exception as ex:
        print("  %-14s ERR %s" % (tag, ex))
print()

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
A_tex = atl(r"F:\sr2-cn\vpp_backup\textures.vpp_pc.orig", "fnt_chinese", None, 2048, 2048)
A_my = atl(os.path.join(G, "patch.vpp_pc"), "fnt_chinese", "g_peg_pc", 2048, 2048)

MYCELLS = np.stack([A_my[1+31*(j//65):1+31*(j//65)+31, 1+31*(j%65):1+31*(j%65)+31].astype(np.int16)
                    for j in range(len(M))])

def ident(cell):
    c = cell.astype(np.int16)
    d = np.abs(MYCELLS - c[None]).sum(axis=(1, 2))
    j = int(d.argmin())
    return chr(M[j]) if 32 <= M[j] < 0x110000 else "?"

def cell(A, u, v):
    if v + 31 > A.shape[0] or u + 31 > A.shape[1]:
        return np.zeros((31, 31), np.uint8)
    return A[v:v+31, u:u+31]

R = [0x4F60, 0x7684, 0x5F1F, 0x5144, 0x4EEC, 0x9700, 0x8981, 0x4F60, 0x7684, 0x4FDD, 0x62A4]
idxM = [M.index(c) for c in R]
idxO = [O.index(c) if c in O else 0 for c in R]
print("target on screen: 任璨偶巧位雄衡任璨伪该")
print()
for an, A in (("texOrig", A_tex),):
    for un, U, V in (("my_uv", myU, myV), ("off_uv", ofU, ofV)):
        for inn, idx in (("@M", idxM), ("@O", idxO)):
            out = []
            for i in idx:
                if i >= len(U):
                    out.append("?"); continue
                out.append(ident(cell(A, U[i], V[i])))
            print("%-8s %-7s %-3s -> %s" % (an, un, inn, "".join(out)))
