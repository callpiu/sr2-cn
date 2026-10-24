import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
d = bytes(v.read(v.find("static_CH","le_strings")))
# @93130 附近的原始字节
off = 93130
print("=== @%d 原始字节 ===" % off)
print("  off-16 .. off+16: %s" % d[off-16:off+16].hex(" "))
print()
u, end = read_units(d, off+8)
print("read_units(d, %d) -> %d 个单元" % (off+8, len(u)))
print("  前 12 个 (值, 字节位置): %s" % [(hex(x), p) for x,p in u[:12]])
print()
# 用大端解第一段
vals = [x for x,_ in u]
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
print("  大端解码: %r" % "".join(S.get(x,"·") for x in vals[:20]))
print()
# 那 '的' 是怎么存的？'的' 在字表的索引
cp_de = ord("的")
print("  '的' U+%04X 在字表: %s  索引 %s  slot %s" % (cp_de, cp_de in CPS, CPS.index(cp_de) if cp_de in CPS else "-", (CPS.index(cp_de)+0x20) if cp_de in CPS else "-"))
print("  第一个单元的值 = 0x%04X = %d" % (vals[0], vals[0]))
print("  原始字节前 4 个: %s" % d[off+8:off+12].hex(" "))
