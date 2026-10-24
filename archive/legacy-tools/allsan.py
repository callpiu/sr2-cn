import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,off_at,offs = file_offsets(d)
print("=== 含「丈」的记录 ===")
n = 0
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    if "丈" in t:
        n += 1
        k = t.index("丈")
        print("  @%-9d len=%-4d  ...%s..." % (off, len(vals), t[max(0,k-25):k+25].replace("\n"," ")))
        print("            槽位: %s -> %s" % (vals[max(0,k-3):k+3], "丈" if vals[k]==270 else vals[k]))
print("  共 %d 条" % n)
print()
print("=== 含「三王」的记录 ===")
n = 0
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    if "三王" in t:
        n += 1
        k = t.index("三王")
        print("  @%-9d ...%s..." % (off, t[max(0,k-25):k+25].replace("\n"," ")))
print("  共 %d 条" % n)
