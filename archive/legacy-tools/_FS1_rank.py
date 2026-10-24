import sys, os, bisect
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")
sM = sorted(M); sO = sorted(O)

pairs = [(0x4F60, 0x4EFB), (0x7684, 0x74A8), (0x5F1F, 0x5076), (0x5144, 0x5DE7),
         (0x4EEC, 0x4F4D), (0x9700, 0x96C4), (0x8981, 0x8861), (0x4FDD, 0x4F2A), (0x62A4, 0x8BE5)]

def test(name, fn):
    out = []; ok = 0
    for r, w in pairs:
        try:
            g = fn(r)
        except Exception:
            g = None
        hit = (g == w); ok += hit
        out.append(chr(g) if g and 32 <= g < 0x110000 else "?")
    print("%-28s %d/9  %s" % (name, ok, "".join(out)))

def rk(T, c):
    return bisect.bisect_left(T, c)

test("M[rank_sorted_M(R)]", lambda r: M[rk(sM, r)] if rk(sM, r) < len(M) else None)
test("sM[M.index(R)]", lambda r: sM[M.index(r)])
test("O[rank_sorted_M(R)]", lambda r: O[rk(sM, r)] if rk(sM, r) < len(O) else None)
test("M[rank_sorted_O(R)]", lambda r: M[rk(sO, r)] if r in O else None)
test("sO[M.index(R)]", lambda r: sO[M.index(r)] if M.index(r) < len(sO) else None)
test("M[O.index(R)]", lambda r: M[O.index(r)] if r in O else None)
test("O[M.index(R)]", lambda r: O[M.index(r)] if M.index(r) < len(O) else None)
test("sM[rank_sorted_M(R)]", lambda r: sM[rk(sM, r)] if rk(sM, r) < len(sM) else None)

# 观察量：屏幕上 G 在 M 中的 index
WR = [0x4EFB, 0x74A8, 0x5076, 0x5DE7, 0x4F4D, 0x96C4, 0x8861, 0x4EFB, 0x74A8, 0x4F2A, 0x8BE5]
RG = [0x4F60, 0x7684, 0x5F1F, 0x5144, 0x4EEC, 0x9700, 0x8981, 0x4F60, 0x7684, 0x4FDD, 0x62A4]
print()
print("R          idxM(R)  G          idxM(G)  rank_sorted(R)  rank_sorted(G)")
for r, w in zip(RG, WR):
    print("%-9s  %-7d  %-9s  %-7d  %-14d  %-14d" % (
        hex(r), M.index(r), hex(w), M.index(w), rk(sM, r), rk(sM, w)))
