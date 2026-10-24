import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

for tag, p in [
    ("原版", r"F:\sr2-cn\pristine\patch.vpp_pc"),
    ("现役", r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"),
]:
    if not os.path.exists(p):
        print(tag, "MISSING", p); continue
    v = Vpp(p)
    print("=" * 72)
    print(tag, os.path.basename(p), os.path.getsize(p), "bytes  entries=", len(v.entries()))
    print("-" * 72)
    for en in v.entries():
        n, e, sz = en["name"], en["ext"], en["size"]
        ln = n.lower()
        if ("charlist" in ln or ln.startswith("fnt") or "le_strings" in ln
                or "font" in ln or ln.endswith(".cxt")):
            print("   %-32s %-12s %10d" % (n, e, sz))