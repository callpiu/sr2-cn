import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
print("=== patch.vpp_pc 里的 le_strings / xtbl ===")
for e in v.entries():
    if e["ext"] in ("le_strings","txt") or e["ext"]=="":
        print("  %-34s %-12s %9d" % (e["name"][:34], e["ext"], e["size"]))
print()
# 松散文件
print("=== 松散文件 ===")
for root in (G, os.path.join(G,"Mods"), os.path.join(G,"Mods","JUICED - Strings"), os.path.join(G,"DLC","Text")):
    if not os.path.isdir(root): continue
    for f in sorted(os.listdir(root)):
        p = os.path.join(root,f)
        if os.path.isfile(p) and f.endswith((".le_strings",".cxt",".xtbl")):
            print("  %-50s %9d" % (os.path.relpath(p,G), os.path.getsize(p)))
