# -*- coding: utf-8 -*-
"""分析 vf3 Table B 的数值模式"""
import struct
d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
A = 0xBC; A_SIZE = N * 16; B = A + A_SIZE

P = []; Q = []
for i in range(N):
    p, q = struct.unpack_from('<2I', d, B + i * 8)
    P.append(p); Q.append(q)

print("P 前 80:", P[:80])
print("\nQ 前 80:", Q[:80])
print("\nP min/max:", min(P), max(P))
print("Q min/max:", min(Q), max(Q))

# Q-P 分布
from collections import Counter
dd = Counter(q - p for p, q in zip(P, Q))
print("\nQ-P 分布:", dd.most_common(12))

# 找 P 的“重置点”(值变小的地方)
resets = [i for i in range(1, N) if P[i] < P[i-1]]
print("\nP 重置点个数:", len(resets), " 前 20:", resets[:20])
if resets:
    print("重置点间隔:", [b - a for a, b in zip(resets[:20], resets[1:21])])
    print("重置处 P[i-1] -> P[i]:", [(P[i-1], P[i]) for i in resets[:12]])

print("\nP 的 distinct 值个数:", len(set(P)), " Q 的 distinct:", len(set(Q)))
print("P distinct 前 60 排序:", sorted(set(P))[:60])

# 看 P 与 index 的关系
print("\n(P, Q) for i in 0..24:")
for i in range(25):
    print("   %-5d %-6d %-6d   diff=%d" % (i, P[i], Q[i], Q[i]-P[i]))

# Table A 的 (a,b) 分布
aa = Counter(); bb = Counter()
for i in range(N):
    a, b, z, f = struct.unpack_from('<4I', d, A + i * 16)
    aa[a] += 1; bb[b] += 1
print("\nTable A: a 分布 top15:", aa.most_common(15))
print("Table A: b 分布 top15:", bb.most_common(15))
print("Table A: a distinct:", len(aa), " b distinct:", len(bb))
print("Table A a 排序前 40:", sorted(aa)[:40])
