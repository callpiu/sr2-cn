# -*- coding: utf-8 -*-
"""确定 vf3 里 U/V 数组的真实偏移与语义（用 ASCII 段自洽性检验）"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME, "patch.vpp_pc"))
e = v.find("fnt_chinese", "vf3_pc")
o = v.data_start + e['body']
N = struct.unpack_from('<I', v.data, o + 8)[0]
print("patch vf3 N=%d size=%d" % (N, e['size']))
print("\n头部 u32 序列 @0x00..0x40:")
for k in range(0, 0x40, 4):
    print("  %#04x: %d (%#x)" % (k, struct.unpack_from('<I', v.data, o+k)[0], struct.unpack_from('<I', v.data, o+k)[0]))

ro = 0xBC; uo = ro + N*16; vo = uo + N*4
print("\nrecs @%#x (%d bytes)  U @%#x  V @%#x  end=%#x" % (ro, N*16, uo, vo, vo+N*4))
print("\nASCII 段 rec[0..10] 与 U/V:")
for i in range(11):
    r = struct.unpack_from('<4H', v.data, o+ro+i*16)
    u = struct.unpack_from('<H', v.data, o+uo+i*2)[0]
    vv = struct.unpack_from('<H', v.data, o+vo+i*2)[0]
    print("  i=%-3d rec=%s  arr1=%-6d arr2=%-6d" % (i, r, u, vv))

print("\nCJK 段 rec[224..232]:")
for i in range(224, 233):
    r = struct.unpack_from('<4H', v.data, o+ro+i*16)
    u = struct.unpack_from('<H', v.data, o+uo+i*2)[0]
    vv = struct.unpack_from('<H', v.data, o+vo+i*2)[0]
    print("  i=%-3d rec=%s  arr1=%-6d arr2=%-6d" % (i, r, u, vv))

# ASCII 段：arr1 应该是列位置。间距 18 => 网格步长 18（patch 是 31？）
print("\nASCII 段非零 arr1 值:", [struct.unpack_from('<H', v.data, o+uo+i*2)[0] for i in range(0,224) if struct.unpack_from('<H', v.data, o+uo+i*2)[0] not in (0,)][:30])
print("ASCII 段非零 arr2 值:", [struct.unpack_from('<H', v.data, o+vo+i*2)[0] for i in range(0,224) if struct.unpack_from('<H', v.data, o+vo+i*2)[0] not in (0,)][:30])
