import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
raw = v.read(v.find("charlist_CH","txt"))
cps = [int(l) for l in raw.decode("utf-8").split("\n") if l.strip().isdigit()]
print("charlist 条目数: %d" % len(cps))
print("前 40 个码点: %s" % ["0x%02X" % x for x in cps[:40]])
print()
for ch in ".<>img ":
    cp = ord(ch)
    print("  %r U+%04X 在表内: %s   索引: %s" % (ch, cp, cp in cps, cps.index(cp) if cp in cps else "-"))
print()
# 直接看那两份文件的实际槽位
for label, p in (("原版", os.path.join(G,"patch.vpp_pc")), ("修复A2", r"F:\sr2-cn\_fix_candidates\patch_fixA2_noimg.vpp_pc")):
    vv = Vpp(p)
    dd = bytes(vv.read(vv.find("static_CH","le_strings")))
    b,c,oa,offs = file_offsets(dd)
    u,_ = read_units(dd, 93130+8)
    vals = [x for x,_ in u]
    print("=== %s @93130 ===" % label)
    print("  槽位: %s" % vals)
    print("  其中位置 10..34: %s" % vals[10:35])
    print("  这些槽位值是否有非 ASCII: %s" % [x for x in vals[10:35] if x > 0x7f])
    print()
