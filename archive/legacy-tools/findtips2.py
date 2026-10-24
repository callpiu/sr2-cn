import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
C = Vpp(os.path.join(G,"common.vpp_pc"))
print("=== common.vpp_pc 里含 tip / hint / load 的条目 ===")
for e in C.entries():
    n = e["name"].lower()
    if any(k in n for k in ("tip","hint","loading","load_")) and e["ext"] in ("xtbl","le_strings","txt"):
        print("  %-40s %-12s %9d" % (e["name"], e["ext"], e["size"]))
print()
# 在 patch.vpp_pc 的 Menus_text 等里找 GAME_LOADING 对应的中文
v = Vpp(G + r"\patch.vpp_pc")
print("=== patch.vpp_pc 里含 loading/tip/hint 的条目 ===")
for e in v.entries():
    n = e["name"].lower()
    if any(k in n for k in ("tip","hint","loading")) :
        print("  %-40s %-12s %9d" % (e["name"], e["ext"], e["size"]))
