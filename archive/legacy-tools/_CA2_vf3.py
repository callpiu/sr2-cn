# -*- coding: utf-8 -*-
"""解析 fnt_chinese.vf3_pc 的字形记录结构"""
import struct, sys

d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
print("magic", d[:4], "ver", struct.unpack_from('<I', d, 4)[0],
      "count", struct.unpack_from('<I', d, 8)[0])
N = struct.unpack_from('<I', d, 8)[0]
HDR = 0xBC
rec = (len(d) - HDR) // N
print("header 0x%X, record size %d, tail %d" % (HDR, rec, (len(d) - HDR) % N))

print("\n--- 前 8 条记录 (u16 x12) ---")
for i in range(8):
    o = HDR + i * rec
    vals = struct.unpack_from('<12H', d, o)
    print("  #%d  %s" % (i, ' '.join('%5d' % v for v in vals)))

print("\n--- 前 8 条记录 (u32 x6) ---")
for i in range(8):
    o = HDR + i * rec
    vals = struct.unpack_from('<6I', d, o)
    print("  #%d  %s" % (i, ' '.join('%10d' % v for v in vals)))

print("\n--- 每个 u16 槽位在所有记录中的 min/max ---")
for k in range(12):
    lo, hi = 1 << 30, -1
    for i in range(N):
        v = struct.unpack_from('<H', d, HDR + i * rec + k * 2)[0]
        if v < lo: lo = v
        if v > hi: hi = v
    print("  slot%-2d  min=%-6d max=%-6d" % (k, lo, hi))

print("\n--- 每个 u32 槽位在所有记录中的 min/max ---")
for k in range(6):
    lo, hi = 1 << 40, -1
    for i in range(N):
        v = struct.unpack_from('<I', d, HDR + i * rec + k * 4)[0]
        if v < lo: lo = v
        if v > hi: hi = v
    print("  slot%-2d  min=%-12d max=%-12d (max hex %08X)" % (k, lo, hi, hi))
