import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")

pairs = [(0x4F60, 0x4EFB), (0x7684, 0x74A8), (0x5F1F, 0x5076), (0x5144, 0x5DE7),
         (0x4EEC, 0x4F4D), (0x9700, 0x96C4), (0x8981, 0x8861), (0x4FDD, 0x4F2A), (0x62A4, 0x8BE5)]

def g(T, k):
    if 0 <= k < len(T) and 32 <= T[k] < 0x110000:
        return chr(T[k])
    return "-"

print("R    code  want  M[c]  M[c+32] M[c-32] O[c]  O[c-32] O[c+32]")
for r, w in pairs:
    i = M.index(r); c = i + 32
    print("%-5s %-5d %-5s %-5s %-7s %-7s %-5s %-7s %-7s" % (
        chr(r), c, chr(w), g(M, c), g(M, c+32), g(M, c-32), g(O, c), g(O, c-32), g(O, c+32)))

print()
print("--- 也试: 引擎 index = code，图集按 M 顺序 ---")
s = "".join(g(M, M.index(r)+32) for r, _ in pairs)
print("  M[code]      :", s)
s = "".join(g(M, M.index(r)+64) for r, _ in pairs)
print("  M[code+32]   :", s)
s = "".join(g(O, O.index(r)+32) if r in O else "-" for r, _ in pairs)
print("  O[O.code]    :", s)
