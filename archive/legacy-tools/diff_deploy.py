import os, sys, hashlib
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def sig(p):
    d = open(p,'rb').read()
    return hashlib.md5(d).hexdigest().upper(), len(d)
pairs = [("当前部署", "patch.vpp_pc"),
         ("v533_tagfix", "patch.vpp_pc.v533_tagfix_20261012_131656.bak"),
         ("v532_clean",  "patch.vpp_pc.v532_before_exp.bak"),
         ("v531",        "patch.vpp_pc.v531_before_mirror.bak")]
for lab, fn in pairs:
    p = os.path.join(G, fn)
    if not os.path.exists(p): continue
    m, sz = sig(p)
    print("%-14s %12d 字节  MD5 %s" % (lab, sz, m))
print()
# 逐条目比大小：当前部署 vs v533_tagfix
a = Vpp(os.path.join(G,"patch.vpp_pc"))
b = Vpp(os.path.join(G,"patch.vpp_pc.v533_tagfix_20261012_131656.bak"))
da = {(e["name"],e["ext"]): e for e in a.entries()}
db = {(e["name"],e["ext"]): e for e in b.entries()}
print("=== 条目差异（当前 vs v533_tagfix）===")
n = 0
for k in sorted(set(da)|set(db)):
    ea, eb = da.get(k), db.get(k)
    sa = ea["size"] if ea else None
    sb = eb["size"] if eb else None
    if sa != sb:
        print("  %-30s 当前 %-10s v533 %-10s" % ("%s.%s" % (k[0], k[1] or "-"), sa, sb))
        n += 1
print("  共 %d 个条目大小不同" % n)
if n == 0:
    print("  → 所有条目大小相同，差异在条目【内容】或【顺序】")
