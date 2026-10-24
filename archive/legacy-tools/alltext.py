import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"; W = r"F:\sr2-cn"
# 1) 第三方 patch 里含 SUI_ 之外，找 HUD 用的短字符串表
v = Vpp(os.path.join(G,"patch.vpp_pc"))
print("=== patch.vpp_pc 里所有非 lua/非字体的文本类资源 ===")
for e in v.entries():
    if e["ext"] in ("le_strings","xtbl","txt","cxt") or e["ext"]=="":
        print("  %-30s %-12s %9d" % (e["name"], e["ext"] or "-", e["size"]))
