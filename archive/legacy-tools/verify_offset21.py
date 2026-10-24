import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("=== 偏移 21 验证 ===")
for off in (-21, 21):
    print("  偏移 %+d:" % off)
    # REC1 前半段
    idx = [1035, 422, 332, 2667, 2328, 371, 1836, 391, 1190]
    want = "弟兄们需要你的保护"
    got = "".join(chr(cn[i+off]) for i in idx)
    print("    文本索引 %s" % idx)
    print("    字表说:  %s" % want)
    print("    偏移后:  %s" % got)
    print()
# 用完整槽位验证 REC1
print("=== 用实际槽位验证（偏移 -21 = 往低索引走）===")
slots = [1067, 454, 364, 2699, 2328, 403, 1868, 423, 1222]
S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
print("  原始槽位解码: %s" % "".join(S[x] for x in slots))
print("  slot-21 解码: %s" % "".join(S.get(x-21,"?") for x in slots))
print()
print("=== 反向确认：用户看到的乱码由什么槽位产生 ===")
user = "任璨偶巧位雄衡"
want = "弟兄们需要你的"
IDX = {chr(cp): i for i,cp in enumerate(cn)}
for a, b in zip(want, user):
    ia, ib = IDX[a], IDX[b]
    print("  %s(idx %4d) -> %s(idx %4d)   差 %+d" % (a, ia, b, ib, ib-ia))
