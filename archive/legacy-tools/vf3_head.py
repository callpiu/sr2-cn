# -*- coding: utf-8 -*-
"""完整解析 fnt_chinese.vf3_pc 头部，寻找 index/remap 机制"""
import sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
d = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))

N = struct.unpack_from("<i", d, 0x08)[0]
print("size=%d  NumCharacters(0x08)=%d" % (len(d), N))

print("\n### 头部 0x00..0xBC 全部 4 字节字段")
for o in range(0x00, 0xBC, 4):
    i0, = struct.unpack_from("<i", d, o)
    i1, = struct.unpack_from("<i", d, o + 4)
    tag = ""
    if o == 0x00: tag = "  <- magic?"
    if o == 0x04: tag = "  <- ?? (0x00800001)"
    if o == 0x08: tag = "  <- NumCharacters"
    if o == 0x1C: tag = "  <- CharSpacing"
    print("  0x%02X: %11d 0x%08X   %11d 0x%08X%s" % (o, i0, i0 & 0xFFFFFFFF, i1, i1 & 0xFFFFFFFF, tag))

print("\n### 记录区 (0xBC 起, 16B/项) 前 6 项 + 关键 idx")
REC = 0xBC
def rec(i):
    return struct.unpack_from("<iiii", d, REC + i * 16)

for i in list(range(6)) + [238, 239, 981, 1025, 1057, 1190, 1764, 2474]:
    f0, f1, f2, f3 = rec(i)
    print("  idx %5d  rec[0xBC+%-5d] = f0=%-6d f1=%-6d f2=0x%04X f3=%-6d"
          % (i, i * 16, f0, f1, f2 & 0xFFFF, f3))

U0, V0 = 0xAF6C, 0xDB18
print("\n### 边界自洽检查")
print("  记录区尾 = 0x%X   U0 = 0x%X   (差 %d)" % (REC + N * 16, U0, U0 - REC - N * 16))
print("  U 尾     = 0x%X   V0 = 0x%X   (差 %d)" % (U0 + N * 4, V0, V0 - U0 - N * 4))
print("  V 尾     = 0x%X   EOF= 0x%X   (差 %d)" % (V0 + N * 4, len(d), len(d) - V0 - N * 4))

print("\n### U/V 数组关键项 (idx -> 图集像素坐标)")
for i in [238, 239, 981, 1025, 1057, 1190, 1764, 2474, 0, 1, 44, 45]:
    u, = struct.unpack_from("<i", d, U0 + i * 4)
    vv, = struct.unpack_from("<i", d, V0 + i * 4)
    print("  idx %5d  U=%-6d V=%-6d  -> cell(%d,%d)" % (i, u, vv, u // 31, vv // 31))