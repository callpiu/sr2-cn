import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
T = 0x69AD7
print("=== 记录头（0x69AD7 = %d）前后 64 字节 ===" % T)
print("  前 32 字节: %s" % d[T-32:T].hex(" "))
print("  含目标 32 字节: %s" % d[T:T+32].hex(" "))
print()
# 从 T-2 开始按 16 位解出连续值
vals = struct.unpack_from("<24H", d, T-12)
print("从 T-12 起的 24 个 16 位值: %s" % list(vals))
print("  解码: %r" % "".join(S.get(x,"·") for x in vals))
print()
# 向前找 00 00 终止符，向后找 00 00
start = T
while start > 0 and d[start-2:start] != b"\x00\x00":
    start -= 2
end = T
while end < len(d)-1 and d[end:end+2] != b"\x00\x00":
    end += 2
print("记录范围: %d .. %d (%d 字节 = %d 个槽位)" % (start, end, end-start, (end-start)//2))
raw = list(struct.unpack_from("<%dH" % ((end-start)//2), d, start))
print("  槽位: %s" % raw)
print("  解码: %r" % "".join(S.get(x,"·") for x in raw))
print()
# 记录头（在 start 之前）
print("=== 记录头（start 前 24 字节）===")
print("  %s" % d[start-24:start].hex(" "))
h = struct.unpack_from("<III", d, start-12)
print("  3 个 u32: %s" % [hex(x) for x in h])
