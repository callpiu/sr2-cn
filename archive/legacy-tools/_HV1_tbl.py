# -*- coding: utf-8 -*-
import os, sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
d = v.read(v.find("fnt_chinese", "vf3_pc"))
N = struct.unpack_from("<I", d, 8)[0]
print("N =", N, "len =", len(d))

# 1) 找出所有 dword 变化点，推断记录边界
dw = [struct.unpack_from("<I", d, o)[0] for o in range(0, len(d)-3, 4)]
print("dwords:", len(dw))
changes = [k for k in range(1, len(dw)) if dw[k] != dw[k-1]]
print("变化点数:", len(changes))
print("前 40 个变化点的 dword 索引:", changes[:40])
print("相邻间隔(去重):", sorted(set(changes[i+1]-changes[i] for i in range(min(400,len(changes)-1))))[:20])

# 2) 打印 0xB8 起的 60 个 dword
print("\n0xB8 起 dwords:")
for k in range(0, 60, 10):
    print("  +%4d: %s" % (4*k, dw[k:k+10]))

# 3) 假设表 = 每字形 4 字节，起始 = first_change_after_header
start_dw = None
for k in range(40, 80):
    if dw[k] == dw[k+1] == 0:
        continue
    start_dw = k; break
print("\n候选表起始 dword 索引:", start_dw)
if start_dw:
    base = start_dw*4
    print("起始字节偏移:", hex(base), base)
    print("剩余字节:", len(d)-base, " /N =", (len(d)-base)/N, " /(N*2) =", (len(d)-base)/(N*2))
    # 取 4 字节步距的表，看前 20 与关键索引
    tbl = [struct.unpack_from("<I", d, base+4*k)[0] for k in range(min(N, (len(d)-base)//4))]
    print("表长:", len(tbl), " 前 20:", tbl[:20])
    for k in [94,95,96,336,354,362,371,391,410,422,967,1035,1190,1784,1836,2268,2296,2342,2656,2667,2794]:
        if k < len(tbl):
            t = tbl[k]
            print("   k=%4d tbl=%-8d  1+31*(k%%65)=%-6d  匹配=%s" % (k, t, 1+31*(k%65), t==1+31*(k%65)))
