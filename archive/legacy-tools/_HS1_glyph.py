# -*- coding: utf-8 -*-
import os, sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
d = v.read(v.find("fnt_chinese", "vf3_pc"))
N = struct.unpack_from("<I", d, 8)[0]
print("N =", N, " len =", len(d))
print("header 0xB8 = 184; (len-184)/N =", (len(d)-184)/N)

def rec(k, base=184, sz=24):
    o = base + sz*k
    return d[o:o+sz]

print("\n=== 前 6 个字形记录 (24B) ===")
for k in range(6):
    r = rec(k)
    print("  k=%d  %s" % (k, ' '.join('%02x'%b for b in r)))

print("\n=== 关键字形记录 ===")
for k in [0,1,32,33,94,95,336,354,362,371,391,410,422,967,1035,1190,1784,1836,2268,2296,2342,2656,2667,2794]:
    r = rec(k)
    u = struct.unpack_from("<6I", r)
    s = struct.unpack_from("<12H", r)
    print("  k=%4d  dwords=%s" % (k, u))
    print("           words =%s" % (s,))

print("\n=== 用 24B 记录反推 (x,y) 候选：找 k=371 与 k=336 ===")
for k in (371, 336, 391, 354, 1035, 410, 422, 967):
    r = rec(k)
    print("  k=%4d bytes: %s" % (k, ' '.join('%02x'%b for b in r)))
