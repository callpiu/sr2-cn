import os, sys
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
targets = ("map_mp_bor", "map_mp_")
for vf in ("patch.vpp_pc","common.vpp_pc","pegs.vpp_pc"):
    p = os.path.join(G,vf)
    if not os.path.exists(p): continue
    try: v = Vpp(p)
    except Exception as ex: print("  %s 打不开" % vf); continue
    hits = [(e["name"], e["ext"], e["size"]) for e in v.entries()
            if any(t in e["name"].lower() for t in targets)]
    print("=== %s: 含 map_mp_ 的条目 %d 个 ===" % (vf, len(hits)))
    for n_,ex,s in hits[:20]:
        print("    %-40s %-10s %d" % (n_, ex or "-", s))
    print()
