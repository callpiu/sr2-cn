import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import CharList, file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
CL = CharList(CPS)
print("=== patch.vpp_pc 里所有含字符串表的资源 ===")
for e in v.entries():
    if e["ext"] in ("le_strings","xtbl","cxt","lua","txt") or "string" in e["name"].lower():
        print("  %-34s %-12s %9d" % (e["name"], e["ext"], e["size"]))
