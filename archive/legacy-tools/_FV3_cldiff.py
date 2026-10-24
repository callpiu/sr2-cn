"""FV3: compare the reference charlist entry sequence with ours.
"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
REF = r"F:\sr2-cn\_ref92\黑道圣徒2简体汉化补丁\patch.vpp_pc"

def load(path):
    v = Vpp(path); e = v.find("charlist_CH", "txt")
    return v.read(e)

a = load(REF)
b = load(os.path.join(G, "patch.vpp_pc"))

A = [int(x) for x in re.findall(rb"\d+", a)]
B = [int(x) for x in re.findall(rb"\d+", b)]
print("ref  numbers=%d  first10=%s  last5=%s" % (len(A), A[:10], A[-5:]))
print("mine numbers=%d  first10=%s  last5=%s" % (len(B), B[:10], B[-5:]))

# strip header from mine
B2 = B[B.index(2795)+1:] if 2795 in B else B
print("mine after dropping header nums: %d  first10=%s" % (len(B2), B2[:10]))

# also line-based parse of mine
lines = [l.strip() for l in b.decode("utf-8", "replace").replace("\r", "").split("\n")]
B3 = [int(l) for l in lines if l.isdigit()]
print("mine line-parse (digits only): %d  first10=%s" % (len(B3), B3[:10]))

print()
print("== ref sequence vs mine(M) ==")
for i in (0, 1, 2, 90, 95, 96, 100, 200, 224, 300, 336, 371, 400, 1000, 1836, 2794):
    ra = A[i] if i < len(A) else None
    mb = B2[i] if i < len(B2) else None
    print("   i=%-5d ref=%-8s mine=%-8s %s" % (i, ra, mb, "OK" if ra == mb else "DIFF"))

diff = [i for i in range(min(len(A), len(B2))) if A[i] != B2[i]]
print()
print("total entry diffs:", len(diff), "of", min(len(A), len(B2)))
for i in diff[:30]:
    print("   i=%-5d ref=%-8d mine=%-8d  %s vs %s" % (i, A[i], B2[i], chr(A[i]) if A[i] > 31 else "?", chr(B2[i]) if B2[i] > 31 else "?"))

# where are the "correct" chars in ref?
print()
for cp, nm in [(0x4F60, "你"), (0x4EFB, "任"), (0x7684, "的"), (0x74A8, "璨"),
               (0x5F1F, "弟"), (0x5076, "偶"), (0x5144, "兄"), (0x5DE7, "巧"),
               (0x4EEC, "们"), (0x4F4D, "位"), (0x9700, "需"), (0x96C4, "雄"),
               (0x8981, "要"), (0x8861, "衡"), (0x4FDD, "保"), (0x4F2A, "伪"),
               (0x62A4, "护"), (0x8BE5, "该"), (0x51FB, "击"), (0x88AD, "袭")]:
    print("   %s U+%04X   ref idx=%-6s mine idx=%-6s" % (
        nm, cp, A.index(cp) if cp in A else "-", B2.index(cp) if cp in B2 else "-"))
