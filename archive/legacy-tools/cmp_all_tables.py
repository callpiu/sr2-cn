import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
paths = {"官方(patch.official_bak)": os.path.join(G,"patch.vpp_pc.official_bak"),
         "实验A备份": r"F:\sr2-cn\_experiment_A_backup\root\patch.vpp_pc"}
tables = {}
for lab, p in paths.items():
    if not os.path.exists(p): continue
    vv = Vpp(p)
    t = [int(l) for l in vv.read(vv.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    tables[lab] = t
    print("%s: %d 项" % (lab, len(t)))
print()
# 活动串的索引（从 static_CH 解出）
idxs = [1035, 422, 332, 2667, 2296, 371, 1836, 391, 1190]
print("活动串用到的索引: %s" % idxs)
print("第三方字表:      %s" % "".join(chr(cn[i]) for i in idxs))
for lab, t in tables.items():
    if max(idxs) < len(t):
        print("%-16s %s" % (lab+":", "".join(chr(t[i]) for i in idxs)))
print()
# 用户看到的乱码
print("用户看到:        任璨偶巧位雄衡  (前半段)")
print("期望:            弟兄们需要你的保护")
