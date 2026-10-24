# -*- coding: utf-8 -*-
"""★ 关键：common.vf3 的 U/V 也是【像素坐标】吗？换个解码方式验证

common 的 ASCII 段 U = 2,0,20,0,38,0,... 交替出现 0！
=> 说明 common 的 U 数组 **不是** 每项都有效；可能是 stride 不对，
   或 common 的 U 数组起始偏移不是 0xB21C。

检验：若 common 的 U 数组是 u16 但按 **u32** 存（低16有效，高16=0），
      则实际排列是 U = [2, 20, 38, 56, ...]（步长18）—— 与 ASCII 行0间距18吻合！
抽查：u16 视图 = 2,0,20,0,38,0  →  u32 视图 = [2, 20, 38, ...]  ✓
"""
import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def dump(path):
    v = Vpp(path); e = v.find("fnt_chinese", "vf3_pc"); o = v.data_start + e['body']
    N = struct.unpack_from('<I', v.data, o + 8)[0]
    inner = struct.unpack_from('<I', v.data, o + 0x10)[0]
    return v, o, N, inner

for tag, path in (("patch", os.path.join(G, "patch.vpp_pc")),
                  ("common", os.path.join(G, "common.vpp_pc"))):
    v, o, N, inner = dump(path)
    print("== %s N=%d inner=%d" % (tag, N, inner))
    # 尝试两种 U 数组布局
    for hdr, name in ((0xBC, "0xBC"), (0xD0, "0xD0")):
        uo = hdr + N * 16
        if uo + N*4 > e_size if False else False: pass
        U16 = [struct.unpack_from('<H', v.data, o+uo+i*2)[0] for i in range(8)]
        U32 = [struct.unpack_from('<I', v.data, o+uo+i*4)[0] for i in range(8)]
        print("   hdr=%s u16[0:8]=%s" % (name, U16))
        print("             u32[0:8]=%s" % (U32))

# 决定性检验：common 的 U 若按 u32 读，前 8 项应 = 2,20,38,56,74,92,110,128（步长18，行0）
# 而且行0有 120 个字形 -> 2 + 18*119 = 2144；行1 起 x=1,14,27...
print("\n★ 若 common U 是 u32（低16有效）:")
v, o, N, inner = dump(os.path.join(G, "common.vpp_pc"))
uo = 0xBC + N*16
U32 = [struct.unpack_from('<I', v.data, o+uo+i*4)[0] for i in range(130)]
print("   U32[0:12] =", U32[:12])
print("   U32[115:125] =", U32[115:125])
print("   U32[125:135] =", U32[125:135])
d = [U32[i+1]-U32[i] for i in range(0, 30, 2)]
print("   偶数项步长:", d)
