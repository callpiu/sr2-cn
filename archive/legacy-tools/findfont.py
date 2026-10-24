import sys, os
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
for f in ("patch.vpp_pc","chunks1.vpp_pc","chunks2.vpp_pc","chunks3.vpp_pc","chunks4.vpp_pc"):
    p = os.path.join(G,f)
    if not os.path.exists(p): print(f,"缺失"); continue
    v = Vpp(p)
    for e in v.entries():
        if "fnt" in e["name"].lower() or "charlist" in e["name"].lower():
            print("%-16s %-22s %-12s %d" % (f, e["name"], e["ext"], e["size"]))
