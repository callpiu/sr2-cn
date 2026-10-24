import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = set(cn)
print("=== 候选探针字 ===")
for w in ("壹贰叁","甲乙丙丁","天地人","水火土","你我他","上下中","大小多","来去看","一二三","狗猫鸟"):
    ok = [c for c in w if ord(c) in S]
    miss = [c for c in w if ord(c) not in S]
    print("  %-8s 可用 %-6s 缺失 %s" % (w, "".join(ok) or "-", "".join(miss) or "-"))
print()
# 找索引连续、视觉可辨的三字组合
print("=== 找几个索引接近的常用字（便于后续反查映射）===")
# 一 二 三 的索引
for ch in "一二三四五十":
    if ord(ch) in S:
        print("  %s 索引 %d" % (ch, cn.index(ord(ch))))
