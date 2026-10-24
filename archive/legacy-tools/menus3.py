import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
d = bytes(v.read(v.find("Menus_text")))
s = d.decode("utf-8", "replace")
print("=== 前 700 字符 ===")
print(s[:700])
print()
print("=== 是否含 SUI_OPTIONS_TITLE / SUI_LOADING ===")
for k in ("SUI_OPTIONS_TITLE","SUI_LOADING","SUI_OPTIONS_WEAPON_SWITCH_SOUND","音效音量"):
    print("  %-34s %s" % (k, "有" if k in s else "无"))
