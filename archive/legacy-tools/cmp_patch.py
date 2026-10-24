import os, sys, hashlib
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OFFICIAL = os.path.join(G, "patch.vpp_pc")                      # 刚校验的官方版
CNPATCH  = r"F:\sr2-cn\_experiment_A_backup\root\patch.vpp_pc"  # 汉化版
a = Vpp(OFFICIAL); b = Vpp(CNPATCH)
print("官方繁中: %d 条目, %d 字节" % (a.num, os.path.getsize(OFFICIAL)))
print("汉化补丁: %d 条目, %d 字节" % (b.num, os.path.getsize(CNPATCH)))
print()
# 建立 名字+扩展 索引
def idx(v):
    d = {}
    for e in v.entries():
        d[(e["name"], e["ext"])] = e
    return d
ia, ib = idx(a), idx(b)
only_a = sorted(set(ia) - set(ib))
only_b = sorted(set(ib) - set(ia))
print("仅官方有的条目: %d" % len(only_a))
for k in only_a[:15]: print("    %s.%s" % k)
print("仅汉化有的条目: %d" % len(only_b))
for k in only_b[:15]: print("    %s.%s" % k)
print()
# 逐条比对内容
same = 0; diff = []
for k in sorted(set(ia) & set(ib)):
    ea, eb = ia[k], ib[k]
    if ea["size"] != eb["size"]:
        diff.append((k, ea["size"], eb["size"], "大小不同")); continue
    da = bytes(a.read(ea)); db = bytes(b.read(eb))
    if da == db: same += 1
    else:
        n = sum(1 for x,y in zip(da,db) if x!=y)
        diff.append((k, ea["size"], eb["size"], "%d 字节不同" % n))
print("内容相同的条目: %d" % same)
print("内容不同的条目: %d" % len(diff))
for k, sa, sb, why in diff[:30]:
    print("    %-28s %-10s 官方 %-10d 汉化 %-10d %s" % (k[0], k[1] or "-", sa, sb, why))
