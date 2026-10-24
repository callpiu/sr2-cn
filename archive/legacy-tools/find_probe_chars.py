import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i,cp in enumerate(cn)}
cands = "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉天地玄黄宇宙洪荒日月盈昃辰宿列张寒来暑往"
print("总项数 %d" % len(cn))
print()
print("%-4s %-8s %s" % ("字","索引","状态"))
for c in cands:
    if ord(c) in IDX:
        print("%-4s %-8d 在表内" % (c, IDX[c]))
    else:
        print("%-4s %-8s 不在表内" % (c, "-"))
print()
# 找一些在表内的、跨度大的常用字
print("=== 按索引采样（每 130 个取一个）===")
picks = []
for target in range(120, 2780, 130):
    if target < len(cn):
        ch = chr(cn[target])
        if 0x4e00 <= ord(ch) <= 0x9fff:
            picks.append((target, ch))
print("  %s" % ["%d:%s" % (i,c) for i,c in picks])
print()
print("可用测试串: %s" % "".join(c for _,c in picks))
print("对应索引:   %s" % [i for i,_ in picks])
