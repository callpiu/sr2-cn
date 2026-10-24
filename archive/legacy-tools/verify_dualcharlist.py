import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
# 简体字表（当前 patch）
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cps_cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
# 原版繁体字表（官方 patch 备份）
OFF = os.path.join(G,"patch.vpp_pc.official_bak")
if not os.path.exists(OFF):
    OFF = r"F:\sr2-cn\_experiment_A_backup\root\patch.vpp_pc"
v2 = Vpp(OFF)
cps_tw = [int(l) for l in v2.read(v2.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("简体字表 %d 项, 繁体字表 %d 项" % (len(cps_cn), len(cps_tw)))
print()
# 核心检验：把简体的 slot 拿去查繁体字表，看是否得到用户报告的乱码字
tests = [("你",0),("的",1),("弟",2),("兄",3),("们",4),("需",5),("要",6),("保",7),("护",8),("出",9),("去",10),("谈",11),("几",12),("笔",13),("生",14),("意",15),("他",16),("免",17),("遭",18),("袭",19),("击",20)]
print("=== 检验：简体 slot 在繁体字表里查出的字 ===")
print("  %-4s %-8s %-8s %-8s %s" % ("字","简体idx","slot","繁体同slot","用户看到的乱码"))
expect = {"你":"任","的":"璨","弟":"偶","兄":"巧","们":"位","需":"雄","要":"衡","保":"伪","护":"该","出":"衡","去":"勾","谈":"远","几":"藐","笔":"乱","生":"携","意":"伪","他":"通","免":"匪","遭":"冰","袭":"挺","击":"拮"}
hit = 0
for ch, order in tests:
    if ord(ch) not in cps_cn: continue
    i = cps_cn.index(ord(ch))
    slot = i + 0x20
    tw = chr(cps_tw[i]) if i < len(cps_tw) else "?"
    exp = expect.get(ch,"?")
    mark = "✓ 命中!" if tw == exp else ""
    if tw == exp: hit += 1
    print("  %-4s %-8d %-8d %-8s %-8s %s" % (ch, i, slot, tw, exp, mark))
print()
print("命中 %d / %d" % (hit, len(tests)))
