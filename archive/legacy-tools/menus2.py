import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
e = v.find("Menus_text")
d = bytes(v.read(e))
print("Menus_text %d 字节, 前 48 字节: %s" % (len(d), d[:48].hex(" ")))
print()
# 直接当 16 位小端序列看
vals = struct.unpack_from("<%dH" % (min(len(d),400)//2), d)
print("前 40 个 16 位值: %s" % list(vals[:40]))
print()
# 用 charlist 当槽位解（值-0x20 作为索引）
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
for base in (0, 4):
    s = "".join(chr(CPS[x-0x20]) if 0x20 <= x-0x20 < len(CPS) else "." for x in vals[base:base+60])
    print("按槽位解(偏移%d): %r" % (base, s))
print()
for base in (0,4):
    s = "".join(chr(x) if 0x20 <= x < 0x10000 else "." for x in vals[base:base+60])
    print("按码点解(偏移%d): %r" % (base, s))
