import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    if e is None: return None
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

P = os.path.join(G, "patch.vpp_pc")
M = cl(P, "charlist_CH")
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")
JP = cl(P, "charlist_JP")
SK = cl(P, "charlist_SK")
CZ = cl(P, "charlist_CZ")
RU = cl(P, "charlist_RU")
PL = cl(P, "charlist_PL")

pairs = [(0x4F60, 0x4EFB), (0x7684, 0x74A8), (0x5F1F, 0x5076), (0x5144, 0x5DE7),
         (0x4EEC, 0x4F4D), (0x9700, 0x96C4), (0x8981, 0x8861), (0x4FDD, 0x4F2A), (0x62A4, 0x8BE5)]

print("R      G      iM     iO     iM(G)  iO(G)")
for r, w in pairs:
    print("%-6s %-6s %-6d %-6s %-6s %-6s" % (
        hex(r), hex(w), M.index(r),
        O.index(r) if r in O else "-",
        M.index(w) if w in M else "-",
        O.index(w) if w in O else "-"))
print()

idxM = [M.index(r) for r, _ in pairs]
idxO = [O.index(r) if r in O else None for r, _ in pairs]

tables = [("M", M), ("O", O), ("JP", JP), ("SK", SK), ("CZ", CZ), ("RU", RU), ("PL", PL),
          ("sortedM", sorted(M)), ("sortedO", sorted(O))]
for base_name, base in (("idx=M", idxM), ("idx=O", idxO)):
    print("--- using %s ---" % base_name)
    for name, T in tables:
        if T is None: continue
        ok = 0; res = []
        for (r, w), i in zip(pairs, base):
            if i is None or i >= len(T):
                res.append("-"); continue
            v = T[i]
            hit = (v == w); ok += hit
            res.append("%s%s" % (chr(v) if 32 <= v < 0x110000 else "?", "*" if hit else ""))
        if ok >= 2:
            print("   %-9s %d/9  %s" % (name, ok, " ".join(res)))
    print()

# 若 idx = M.index(R)，求 T[i] 的值，看 T 是否是 M 的某种重排
print("needed T values: " + ", ".join("%d:%s" % (i, chr(w)) for i, (_, w) in zip(idxM, pairs)))
print()
print("M around those indices:")
for i, (r, w) in zip(idxM, pairs):
    lo = max(0, i - 3); hi = min(len(M), i + 4)
    print("  i=%-5d want=%s   M[%d:%d]=%s" % (i, chr(w), lo, hi, "".join(chr(c) for c in M[lo:hi])))
