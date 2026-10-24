"""FV1: reverse-engineer the RUNTIME charlist R.

atlas[k] == M[k] (verified visually).  The engine draws slot S for code c.
On screen we saw  char = M[S]  while the correct char is M[c-32].
=> R[c-32] = M[S]  with S = M.index(screen_char).
So R is a permutation of M.  Compare R against the official charlist O.
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")
print("len(M)=%d len(O)=%d" % (len(M), len(O)))

# (code, correct_char, screen_char)  -- from the two broken subtitles
DATA = [
    (403, 0x4F60, 0x4EFB), (1868, 0x7684, 0x74A8), (1067, 0x5F1F, 0x5076),
    (454, 0x5144, 0x5DE7), (364, 0x4EEC, 0x4F4D), (2699, 0x9700, 0x96C4),
    (2328, 0x8981, 0x8861), (423, 0x4FDD, 0x4F2A), (1222, 0x62A4, 0x8BE5),
    # second string extras
    (510, 0x51FA, 0x51FA), (613, 0x53BB, 0x53BB),
]

print()
print("code  c-32  M[c-32]  correct  screen  M.idx(screen)  O.idx(correct)  O.idx(screen)")
for c, corr, scr in DATA:
    i = c - 32
    m = M[i] if i < len(M) else -1
    oi = O.index(corr) if corr in O else -1
    os_ = O.index(scr) if scr in O else -1
    print("%-5d %-5d U+%04X   U+%04X   U+%04X  %-14d %-15d %d" % (
        c, i, m, corr, scr, M.index(scr) if scr in M else -1, oi, os_))

print()
print("R[c-32] == screen ?  (R = M with slots swapped)")
for c, corr, scr in DATA:
    i = c - 32
    print("  R[%d] = M[%d] = U+%04X  screen U+%04X  %s" % (
        i, M.index(scr), M[M.index(scr)], scr, "OK" if M[M.index(scr)] == scr else "NO"))

print()
print("Is O identical to M up to those slots?  compare elementwise")
diff = [k for k in range(min(len(M), len(O))) if M[k] != O[k]]
print("  first 40 mismatching indices:", diff[:40])
print("  total mismatches:", len(diff))
for k in diff[:40]:
    print("    idx %-6d M=U+%04X  O=U+%04X" % (k, M[k], O[k]))
