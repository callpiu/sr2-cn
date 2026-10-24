import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc.v531_before_mirror.bak"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
slots = [1067, 454, 364, 2699, 2328, 403, 1868, 423, 1222]
USER  = "任璨偶巧位雄衡"
WANT  = "弟兄们需要你的"
print("槽位:      %s" % slots)
print("字表解码:  %s" % "".join(S[x] for x in slots))
print("用户看到:  %s" % USER)
print("应为:      %s" % WANT)
print()
# 用户看到的字在字表里的索引
IDX = {chr(cp): i for i,cp in enumerate(cn)}
print("用户字索引: %s" % [IDX.get(c,-1) for c in USER])
print("期望字索引: %s" % [IDX.get(c,-1) for c in "弟兄们需要你的"])
print("差(用户-槽位+0x20): %s" % [IDX.get(c,-1)-(x-0x20) for c,x in zip(USER,slots)])
print()
# 假设 HUD 索引 = 槽位-0x20+K，K 使 索引 -> 字表该位置的字 = 用户字
print("=== 每个位置要求的 K ===")
for c, x in zip(USER, slots):
    need = IDX.get(c,-1) - (x-0x20)
    print("  %s: 需要 K=%+d" % (c, need))
