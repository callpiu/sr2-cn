# -*- coding: utf-8 -*-
"""★ 决定性分析：把运行期内存里的乱码串 与 磁盘数据 做【双向映射】求解

已知（来自真机内存转储 scan3_20261012_234113.txt）：
  内存里存在的乱码串 = 任(4EFB) 璨(74A8) 偶(5076) 巧(5DE7) 位(4F4D)
  正确文本           = 你(4F60) 的(7684) 弟(5F1F) 兄(5144) 们(4EEC)

两个方向都要试：
  A. slot 直接索引 common vf3(2838)  -> 字形 -> 官方图集  -> 应该等于 正确字 还是 乱码字?
  B. 反过来：在官方图集里找 乱码字 的字形，看它的坐标对应 vf3 里的哪一项
"""
import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
CORRECT = "你的弟兄们需要你的保护"
GARBLE  = "任璨偶巧位雄衡伪该"

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]
print("charlist_CH(2795) 首=%s 末=%s" % (chr(CL[0]), chr(CL[-1])))
c2s = {}; s2c = {}
for i, cp in enumerate(CL):
    slot = i + 0x20
    c2s.setdefault(chr(cp), slot)
    s2c[slot] = chr(cp)
# 索引（非 slot）
c2i = {}
for i, cp in enumerate(CL):
    c2i.setdefault(chr(cp), i)

print("\n正确字 -> charlist 索引/槽位:")
for ch in CORRECT:
    print("   %r idx=%-5s slot=%-5s" % (ch, c2i.get(ch), c2s.get(ch)))
print("\n乱码字 -> charlist 索引/槽位:")
for ch in GARBLE:
    print("   %r idx=%-5s slot=%-5s" % (ch, c2i.get(ch), c2s.get(ch)))

# 逐字比对：正确字的 idx 是否等于乱码字的 idx?
print("\n★ 逐位对照：正确字(idx) vs 乱码字(idx) —— idx 是否相同?")
for a, b in zip(CORRECT, GARBLE):
    ia, ib = c2i.get(a), c2i.get(b)
    print("   %r idx=%-5s  ->  %r idx=%-5s   %s" % (
        a, ia, b, ib, "★相同!" if ia == ib else "(差 %s)" % ((ib-ia) if (ia is not None and ib is not None) else "?")))
