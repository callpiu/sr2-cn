import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
OFFICIAL = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
CNPATCH  = r"F:\sr2-cn\_experiment_A_backup\root\patch.vpp_pc"
a = Vpp(OFFICIAL); b = Vpp(CNPATCH)
def idx(v):
    d = {}
    for e in v.entries(): d[(e["name"], e["ext"])] = e
    return d
ia, ib = idx(a), idx(b)
only_b = sorted(set(ib) - set(ia))
print("=== 汉化新增的 36 个条目 ===")
for k in only_b:
    print("    %-34s %-10s %d 字节" % (k[0], k[1] or "-", ib[k]["size"]))
print()
# 官方版的 static_*/platform_* 覆盖情况
print("=== 官方版里的 static_* / platform_* 条目 ===")
for k in sorted(ia):
    if k[0].startswith(("static_","platform_")):
        print("    %-34s %-10s %d" % (k[0], k[1] or "-", ia[k]["size"]))
