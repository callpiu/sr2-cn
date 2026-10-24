import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def cl(p):
    v = Vpp(p); t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
M = cl(os.path.join(G,"patch.vpp_pc"))
print("OFFICIAL[:40] =", [hex(c) for c in O[:40]])
print("OFFICIAL[33]=U+%04X %s   [65]=U+%04X %s" % (O[33], chr(O[33]), O[65], chr(O[65])))
print("index_O('A'=0x41) =", O.index(0x41) if 0x41 in O else None)
print("index_O('a'=0x61) =", O.index(0x61) if 0x61 in O else None)
print("index_O(0x20) =", O.index(0x20) if 0x20 in O else None)
print()
print("MINE[:40] =", [hex(c) for c in M[:40]])
print("index_M('A') =", M.index(0x41) if 0x41 in M else None)
print()
# 同一字符在两表的 index 差
diffs = {}
for cp in [0x4F60,0x7684,0x5F1F,0x5144,0x9700,0x8981]:
    if cp in O and cp in M:
        print("U+%04X %s  O=%4d  M=%4d  差=%d" % (cp, chr(cp), O.index(cp), M.index(cp), O.index(cp)-M.index(cp)))
