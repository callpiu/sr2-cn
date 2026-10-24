import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, HDR, MAGIC
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,off_at,offs = file_offsets(d)
print("HDR=%d buckets=%d count=%d off_at=%d" % (HDR,b,c,off_at))
print("偏移表前 6 项: %s" % offs[:6])
print()
# 找包含 0x69AD7 的记录
T = 0x69AD7
inc = [o for o in set(offs) if 0 < o <= T and T < o+4000]
print("候选记录起点: %s" % sorted(inc)[:6])
for off in sorted(inc)[:3]:
    u,end = read_units(d, off+8)
    if u is None: 
        print("  @%d read_units 失败" % off); continue
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    print("  @%-9d 长度 %-5d 文本: %s" % (off, len(vals), t[:130]))
    if 270 in vals:
        k = vals.index(270)
        print("       「丈」在位置 %d，上下文: %s" % (k, t[max(0,k-15):k+15]))
