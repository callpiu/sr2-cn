import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
C = Vpp(os.path.join(G,"common.vpp_pc"))
names = [e["name"] for e in C.entries()]
print("common.vpp_pc 里含 achiev / stat / unlock 的条目:")
for e in C.entries():
    n = e["name"].lower()
    if any(k in n for k in ("achiev","unlock","stat")):
        print("  %-40s %-10s %9d" % (e["name"], e["ext"], e["size"]))
