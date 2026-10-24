import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = set(CPS)
print("charlist %d 项, 索引0=%d(%s) 索引360=%d(%s)" % (len(CPS), CPS[0], chr(CPS[0]) if CPS[0]>0x20 else "?", CPS[360], chr(CPS[360])))
print()
# 取 static_CH 的第一条记录
d = open(G + r"\Mods\static_CH.le_strings","rb").read() if os.path.exists(G+r"\Mods\static_CH.le_strings") else bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs = file_offsets(d)
off = sorted(o for o in dict.fromkeys(offs) if 0 < o <= len(d)-10)[5]
u,_ = read_units(d, off+8)
vals = [x for x,_ in u]
print("记录 @%d, %d 个 16 位值" % (off, len(vals)))
print("  前 20 个值: %s" % vals[:20])
print()
# 判断：这些值是码点还是槽位？
as_cp = "".join(chr(x) for x in vals[:30] if x > 0x100)
as_slot = "".join(chr(CPS[x-0x20]) for x in vals[:30] if 0x20 <= x-0x20 < len(CPS))
print("按【码点】解释: %r" % as_cp)
print("按【槽位】解释: %r" % as_slot)
print()
# 统计：所有值中有多少 > 0x100（大概率是码点）
allv = []
for o in list(dict.fromkeys(offs))[:2000]:
    if not (0 < o <= len(d)-10): continue
    uu,_ = read_units(d, o+8)
    if uu is None: continue
    allv += [x for x,_ in uu]
hi = [x for x in allv if x > 0x100]
print("2000 条记录共 %d 个值，其中 > 0x100 的 %d 个 (%.1f%%)" % (len(allv), len(hi), 100*len(hi)/max(1,len(allv))))
print("  >0x100 的值样例: %s" % hi[:15])
print("  这些值是否是合法码点 (在 charlist 里): %d / %d" % (sum(1 for x in hi if x in S), len(hi)))
print("  这些值是否是合法槽位: %d / %d" % (sum(1 for x in hi if 0x20 <= x-0x20 < len(CPS)), len(hi)))
