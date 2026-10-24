# -*- coding: utf-8 -*-
import struct
d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
B = 0xBC + N * 16
P = []; Q = []
for i in range(N):
    p, q = struct.unpack_from('<2I', d, B + i * 8)
    P.append(p); Q.append(q)

resets = [i for i in range(1, N) if P[i] < P[i-1]]
print("resets(%d):" % len(resets), resets)
print()
print("P[1360:1440]:", P[1360:1440])
print()
print("P[2790:2795]:", P[2790:2795])
print("distinct P:", len(set(P)))
print("P 最大值:", max(P))
# 每个 reset 处的前后值
print()
for i in resets:
    print("   reset@%-5d  P[i-1]=%-5d -> P[i]=%-5d   (Q[i-1]=%d, Q[i]=%d)" % (i, P[i-1], P[i], Q[i-1], Q[i]))
