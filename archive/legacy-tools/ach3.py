import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
C = Vpp(os.path.join(G,"common.vpp_pc"))
s = bytes(C.read(C.find("achievements"))).decode("utf-8","replace")
print("achievements.xtbl 前 800 字符:")
print(s[:800])
print()
print("含 SUI_ 吗: %s" % ("SUI_" in s))
print("含 ACHIEVE 吗: %s" % ("ACHIEVE" in s))
