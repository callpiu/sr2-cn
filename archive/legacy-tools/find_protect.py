import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs = file_offsets(d)
print("=== static_CH 里所有含「保护」且长度 15~40 的记录 ===")
rows = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    if "保护" in t and 15 <= len(t) <= 40:
        rows.append((off, len(t), t))
for off, n, t in rows:
    print("  @%-9d len=%-4d %s" % (off, n, t))
print("  共 %d 条" % len(rows))
print()
# 活动开始时显示的提示：搜「保护」+「开始」
print("=== 含「保护」且含「开始/任务/目标」的记录 ===")
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    if "保护" in t and any(k in t for k in ("开始","任务","目标","抵达","前往")):
        print("  @%-9d len=%-4d %s" % (off, len(t), t[:70]))
