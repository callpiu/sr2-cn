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
uniq = sorted(set(o for o in offs if 0 < o <= len(d)-10))
T = 0x69AD7
import bisect
i = bisect.bisect_right(uniq, T) - 1
print("T=%d(0x%X), 记录 [%d..%d), 下一记录 [%d..)" % (T, T, uniq[i], uniq[i+1], uniq[i+1]))
# 实际文本范围
start = uniq[i]+8
end = uniq[i+1]
print("实际文本字节 %d..%d (%d 字节 = %d 槽位)" % (start, end, end-start, (end-start)//2))
vals = list(struct.unpack_from("<%dH" % ((end-start)//2), d, start))
print("  文本: %r" % "".join(S.get(x,"·") for x in vals))
print("  槽位: %s" % vals)
