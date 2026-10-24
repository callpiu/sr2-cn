# -*- coding: utf-8 -*-
"""扫描 vf3 中 0 / 65535 的位置，推断真实记录边界"""
import struct

d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
allv = struct.unpack_from('<%dI' % ((len(d) - 0xBC) // 4), d, 0xBC)
print("u32 count:", len(allv))

pos0 = [i for i, v in enumerate(allv) if v == 0]
posF = [i for i, v in enumerate(allv) if v == 65535]
print("zeros:", len(pos0), " 65535:", len(posF))

def diffs(p, n=25):
    return [b - a for a, b in zip(p[:n], p[1:n+1])]
print("zero idx first 40:", pos0[:40])
print("zero gaps first 40:", diffs(pos0, 40))
print("F idx first 40:", posF[:40])
print("F gaps first 40:", diffs(posF, 40))

print("\n--- 非0非F 的值分布 (前 40) ---")
other = [v for v in allv if v not in (0, 65535)]
print("count:", len(other), " total expected:", len(allv) - 2 * N)
from collections import Counter
c = Counter(other)
print("top 30:", c.most_common(30))
print("min", min(other), "max", max(other))
print("first 60 others:", other[:60])
