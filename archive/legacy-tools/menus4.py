import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
s = bytes(v.read(v.find("Menus_text"))).decode("utf-8","replace")
names = re.findall(r'<Name>([^<]+)</Name>', s)
print("Menus_text 共 %d 个 <Name>" % len(names))
print()
print("=== 含 SUI / OPTION / LOADING / AUDIO / VOLUME 的 ===")
for n in names:
    if any(k in n.upper() for k in ("SUI","LOADING","VOLUME","AUDIO","WEAPON_SWITCH")):
        print("  %s" % n)
print()
print("=== 所有 <Name> 里以 SUI 开头的（前 40）===")
sui = [n for n in names if n.upper().startswith("SUI")]
print("  共 %d 个:" % len(sui))
for n in sui[:40]: print("    %s" % n)
