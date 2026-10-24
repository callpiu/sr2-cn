import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
# 第三方简体字表
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
# 官方繁体字表
OFF = os.path.join(G,"patch.vpp_pc.official_bak")
if not os.path.exists(OFF): OFF = r"F:\sr2-cn\_experiment_A_backup\root\patch.vpp_pc"
v2 = Vpp(OFF)
tw = [int(l) for l in v2.read(v2.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("第三方 %d 项, 官方 %d 项" % (len(cn), len(tw)))
print()
# 检验：第三方字表的索引 i 处，官方字表是什么字？
targets = ["弟","兄","们","需","要","你","的","保","护","出","去","谈","几","笔","生","意","他","免","遭","袭","击"]
print("  %-4s %-6s %-8s %-8s %s" % ("字","索引","第三方字表","官方同索引","图集抠出"))
atlas = {"弟":"弱","兄":"克","们":"份","需":"霸","要":"视","你":"使","的":"盆","保":"俯","护":"抵"}
for ch in targets:
    cp = ord(ch)
    if cp not in cn: 
        print("  %-4s 不在第三方字表" % ch); continue
    i = cn.index(cp)
    tws = chr(tw[i]) if i < len(tw) else "?"
    print("  %-4s %-6d %-8s %-8s %s" % (ch, i, ch, tws, atlas.get(ch,"?")))
