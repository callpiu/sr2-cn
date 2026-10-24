import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,off_at,offs = file_offsets(d)
# 找 @225978 那条
u,end = read_units(d, 225978+8)
vals = [x for x,_ in u]
print("@225978 用 read_units 解: %r" % "".join(S.get(x,"·") for x in vals))
print("  槽位: %s" % vals)
print("  原始字节: %s" % d[225978+8:225978+8+24].hex(" "))
print()
# 用 GBK 直接解这段
raw = d[225978+8:225978+8+40]
print("按 GBK 解: %r" % raw.decode("gbk","replace"))
print()
# 找「辩护律师」的 GBK 字节
gbk = "辩护律师".encode("gbk")
print("辩护律师 GBK = %s" % gbk.hex(" "))
i = d.find(gbk)
print("在 static_CH 里 @ %s" % (i if i>=0 else "未找到"))
if i >= 0:
    print("  上下文(GBK): %r" % d[max(0,i-30):i+30].decode("gbk","replace"))
