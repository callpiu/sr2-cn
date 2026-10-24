# -*- coding: utf-8 -*-
import os, sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def load(path, tag):
    v = Vpp(path)
    e = v.find("fnt_chinese", "vf3_pc")
    d = v.read(e)
    N = struct.unpack_from("<I", d, 8)[0]
    print("=== %s  N=%d  len=%d  (len-0xD0)/N=%.4f  (len-0xD0)/16=%.2f" %
          (tag, N, len(d), (len(d)-0xD0)/N, (len(d)-0xD0)/16))
    return d, N

d, N = load(os.path.join(G, "patch.vpp_pc"), "patch(汉化)")
o, No = load(r"F:/sr2-cn/pristine/patch.vpp_pc", "pristine(官方)")

def rec(d, k, base=0xD0, sz=16):
    return struct.unpack_from("<IIII", d, base + k*sz)

print("\n=== 汉化 vf3 记录 (spacing, byteWidth, offset, kerning) ===")
for k in [0,1,32,33,94,95,336,354,362,371,391,410,422,967,1035,1190,1784,1836,2268,2296,2342,2656,2667,2794]:
    print("  k=%4d  %s" % (k, rec(d, k)))

print("\n=== 官方 vf3 记录 (前 100 内抽样) ===")
for k in [0,1,32,33,94,95,336,354,362,371,391,410,422,967,1035,1190,1784,1836]:
    print("  k=%4d  %s" % (k, rec(o, k)))

# 用 offset 反推 cell：若 offset 是线性像素/字节偏移
print("\n=== 若 offset 是 '线性单元格编号' 或 '像素偏移' ===")
for k in [336,354,362,371,391,410,422,967,1035,1190,1784,1836,2268,2296,2342,2656,2667]:
    sp, bw, off, kern = rec(d, k)
    print("  k=%4d off=%-8d  off/31=%.2f  (off-1)/31=%.2f  off%%65=%d off//65=%d" %
          (k, off, off/31.0, (off-1)/31.0, off % 65, off // 65))
