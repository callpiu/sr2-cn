# -*- coding: utf-8 -*-
"""GG2: dump fnt_chinese.vf3_pc 的真实结构, 验证 U/V 布局与 -5 偏移。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(os.path.join(G, "patch.vpp_pc"))
b = pv.read(pv.find("fnt_chinese", "vf3_pc"))
print("vf3 =", len(b), "bytes")
print("头 0xD0 前 32 字节:", b[:32].hex(" "))
print("hdr@0x00 =", struct.unpack_from("<I", b, 0)[0])
print("N   @0x08 =", struct.unpack_from("<I", b, 8)[0])
print("hdr@0x0C =", struct.unpack_from("<I", b, 12)[0])
print("hdr@0x10 =", struct.unpack_from("<I", b, 16)[0])
print("hdr@0x14 =", struct.unpack_from("<I", b, 20)[0])
print("hdr@0x16 (u16) =", struct.unpack_from("<H", b, 22)[0])
print("hdr@0x18 =", struct.unpack_from("<I", b, 24)[0])

N = struct.unpack_from("<I", b, 8)[0]
REC = 0xD0
UOFF = REC + N * 16
VOFF = UOFF + N * 4
print("\nN=%d  FontChar@0x%X   U@0x%X (%d 项)   V@0x%X (余 %d 字节 = %d 项)"
      % (N, REC, UOFF, N, VOFF, len(b) - VOFF, (len(b) - VOFF) // 4))

print("\n--- FontCharacter 记录 (i: w h a b) ---")
for i in list(range(0, 6)) + list(range(360, 376)) + [2790, 2791, 2792, 2793, 2794]:
    if i * 16 + REC + 16 <= UOFF:
        w, h, a, c = struct.unpack_from("<HHHH", b, REC + i * 16)
        print("   i=%-5d w=%-4d h=%-4d 0x%04X 0x%04X" % (i, w, h, a, c))

U = struct.unpack_from("<%di" % N, b, UOFF)
M = (len(b) - VOFF) // 4
V = struct.unpack_from("<%di" % M, b, VOFF)
print("\n--- U 数组 ---")
print("   U[0:12]  :", U[:12])
print("   U[360:376]:", U[360:376])
print("   唯一值个数:", len(set(U)))
print("   前 70 个差值:", [U[i+1]-U[i] for i in range(0, 70)])
print("\n--- V 数组 ---")
print("   V[0:12]  :", V[:12])
print("   V[360:376]:", V[360:376])
print("   唯一值个数:", len(set(V)))
print("   前 70 个差值:", [V[i+1]-V[i] for i in range(0, min(70, len(V)-1))])

# 验证恒等式 U[j] == 1 + 31*(j%65), V[j] == 1 + 31*(j//65)
okU = sum(1 for j in range(len(U)) if U[j] == 1 + 31 * (j % 65))
okV = sum(1 for j in range(len(V)) if V[j] == 1 + 31 * (j // 65))
print("\n恒等式 U[j]==1+31*(j%%65) : %d/%d" % (okU, len(U)))
print("恒等式 V[j]==1+31*(j//65) : %d/%d" % (okV, len(V)))
