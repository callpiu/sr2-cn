# -*- coding: utf-8 -*-
"""暴力搜索 vf3 字形记录布局"""
import struct

d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
TOTAL = len(d) - 0xBC
print("data bytes after 0xBC:", TOTAL, " /2795 =", TOTAL / 2795.0)

print("\n--- u32 流 (从 0xBC 起, 前 60 个) ---")
vals = struct.unpack_from('<60I', d, 0xBC)
for i in range(0, 60, 10):
    print("  ", vals[i:i+10])

print("\n--- 尝试: stride=24, 视为 (x,y,w,h,adv,bear) u16x12 的前 8 个 ---")
for i in range(8):
    o = 0xBC + i * 24
    print("  #%d %s" % (i, struct.unpack_from('<12H', d, o)))

def test(stride, off, fields, limit=800):
    """fields = 4 个 u16 下标, 解释为 (x, y, w, h)"""
    ok = 0
    for i in range(limit):
        o = off + i * stride
        if o + 8 > len(d):
            return None
        v = struct.unpack_from('<4H', d, o + fields[0]*2)
        x, y, w, h = v
        if 0 <= x <= 2048 and 0 <= y <= 1400 and 1 <= w <= 64 and 1 <= h <= 64 and x + w <= 2048 and y + h <= 1400:
            ok += 1
    return ok

print("\n--- 暴力搜索 (x,y,w,h) 布局 ---")
best = []
for stride in (8, 12, 16, 20, 24):
    for off in range(0x80, 0x100, 2):
        for base in range(0, 12):
            r = test(stride, off, (base, base+1, base+2, base+3), 400)
            if r and r >= 380:
                best.append((r, stride, hex(off), base))
best.sort(reverse=True)
for b in best[:15]:
    print("   hits=%d stride=%d off=%s base=%d" % b)

print("\n--- 尝试: 直接读前 40 个 u32 的分布 ---")
allv = struct.unpack_from('<%dI' % (TOTAL // 4), d, 0xBC)
from collections import Counter
c = Counter(allv)
print("  最常见值:", c.most_common(12))
print("  总数:", len(allv))
big = [v for v in allv if v > 2000 and v != 65535]
print("  大于2000且非65535 的个数:", len(big), "样例:", big[:20])
