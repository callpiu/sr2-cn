import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
# achievement xtbl
for nm in ("achievements","achievements_german"):
    e = v.find(nm)
    if not e: continue
    s = bytes(v.read(e)).decode("utf-8","replace")
    print("=== %s (%d 字节) ===" % (nm, len(s)))
    names = re.findall(r'<Name>([^<]+)</Name>', s)
    print("  <Name> %d 个, 前 10: %s" % (len(names), names[:10]))
    # 找含 SUI_ 的
    sui = sorted(set(re.findall(r'SUI_[A-Z0-9_]+', s)))
    print("  含 SUI_ 引用 %d 个: %s" % (len(sui), sui[:10]))
    # 找含 ACHIEVE 的
    ach = [n for n in names if "ACHIEVE" in n.upper()][:8]
    print("  含 ACHIEVE 的 Name: %s" % ach)
    # 看结构：找 <Text> / <Description> 之类
    tags = sorted(set(re.findall(r'<([A-Za-z_]+)>', s)))
    print("  所有标签: %s" % tags[:25])
    print()
