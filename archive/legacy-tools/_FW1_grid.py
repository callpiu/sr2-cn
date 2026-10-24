"""FW1: the atlas on disk is 65-col.  The engine may compute the cell with a
different column count C (e.g. 66, from the font descriptor).  Brute force
(C, A) so that the glyph the engine lands on equals the screen glyph.

engine slot  s = code-32
engine cell  (col_e, row_e) = (s%C, s//C)
atlas index  k = row_e*A + col_e     (A = real atlas columns)
want         M[k] == screen_char
"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")

PAIRS = [(0x4F60, 0x4EFB), (0x7684, 0x74A8), (0x5F1F, 0x5076), (0x5144, 0x5DE7),
         (0x4EEC, 0x4F4D), (0x9700, 0x96C4), (0x8981, 0x8861), (0x4FDD, 0x4F2A), (0x62A4, 0x8BE5)]

def s_of(corr):
    return M.index(corr) + 32

print("correct  s=code-32  want")
for corr, scr in PAIRS:
    print("  U+%04X  %-6d  U+%04X" % (corr, s_of(corr), scr))

print()
best = []
for C in range(40, 120):
    for A in range(40, 120):
        ok = 0
        for corr, scr in PAIRS:
            s = s_of(corr)
            k = (s // C) * A + (s % C)
            if 0 <= k < len(M) and M[k] == scr:
                ok += 1
        if ok >= 6:
            best.append((ok, C, A))
best.sort(reverse=True)
print("top (C engine cols, A atlas cols):")
for ok, C, A in best[:20]:
    print("  %d/9   C=%-4d A=%-4d" % (ok, C, A))

# also: engine uses code directly (no -32)
print()
print("variant: k = (c//C)*A + (c%C) with c = code (not code-32)")
best2 = []
for C in range(40, 120):
    for A in range(40, 120):
        ok = 0
        for corr, scr in PAIRS:
            c = M.index(corr) + 32
            k = (c // C) * A + (c % C)
            if 0 <= k < len(M) and M[k] == scr:
                ok += 1
        if ok >= 6:
            best2.append((ok, C, A))
best2.sort(reverse=True)
for ok, C, A in best2[:20]:
    print("  %d/9   C=%-4d A=%-4d" % (ok, C, A))
