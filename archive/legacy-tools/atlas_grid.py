import os, sys, struct, collections
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4)) + [0]*(N-nV)
# 按 V 分组
rows = collections.defaultdict(list)
for i in range(N):
    rows[V[i]].append(i)
print("V 值（行）数: %d" % len(rows))
for vv in sorted(rows)[:5]:
    idxs = sorted(rows[vv], key=lambda i: U[i])
    us = [U[i] for i in idxs]
    d = [us[k+1]-us[k] for k in range(min(8,len(us)-1))]
    print("  V=%-6d %3d 个  U范围 %4d..%-4d  相邻差 %s  首索引 %d" % (vv, len(idxs), us[0], us[-1], d, idxs[0]))
print()
# 索引 234 附近
print("索引 230..240 的 (U,V):")
for i in range(230, 241):
    print("    idx %-4d %-3s U=%-5d V=%-5d" % (i, chr(cn[i]) if cn[i]>127 else "·", U[i], V[i]))
print()
# 关键：索引 vs U 的关系
print("=== 索引与 U 的关系（前后各 6 个）===")
for i in [0,1,2,93,94,95,96,230,234,290,293,371,1035]:
    print("  idx %-5d %-3s U=%-5d V=%-5d  行内序号=%d" % (i, chr(cn[i]), U[i], V[i], sorted(rows[V[i]], key=lambda k:U[k]).index(i)))
