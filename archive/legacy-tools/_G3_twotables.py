# -*- coding: utf-8 -*-
"""★★★ 决定性假设：字幕使用的 charlist 与 HUD 不同！

HUD(正确)：直升机突击 / 已完成停靠 / 面包车耐久 / 迷雾巷
字幕(乱码)：你的弟兄们需要你的保护

如果字幕走的是【另一张 charlist】（比如 common 的 2838 表，或官方原版 2838 表），
那么同一 slot 会解出不同的字。

检验：把【乱码字】在 2838 表里的索引 与 【正确字】在 2795 表里的索引 对比
     —— 如果是同一 slot 用了两张表，则 slot 应相同！
"""
import sys, os, struct, json
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL2795 = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
          if s.strip().isdigit()]

# 官方 2838 表
p2838 = r"F:\sr2-cn\_day_2026-10-07\04_规则与数据\_expected_charlist.json"
J2838 = json.load(open(p2838))
print("2795 表 %d 项 / 2838 表 %d 项" % (len(CL2795), len(J2838)))

c2i2795 = {}
for i, cp in enumerate(CL2795):
    c2i2795.setdefault(chr(cp), i)
c2i2838 = {}
for i, cp in enumerate(J2838):
    c2i2838.setdefault(chr(cp), i)

COR = "你的弟兄们需要你的保护"
GAR = "任璨偶巧位雄衡任璨伪该"

print("\n★★ 核心检验：正确字在 2795 表 idx  vs  乱码字在 2838 表 idx")
print("   若两者相等 => 字幕用错表（slot 相同，表不同）")
hits = 0
for i, (a, b) in enumerate(zip(COR, GAR)):
    ia = c2i2795.get(a)
    ib = c2i2838.get(b)
    mark = "★★★ 相同!" if ia == ib else ""
    if ia == ib: hits += 1
    print("  %2d %r 2795idx=%-5s  |  %r 2838idx=%-5s  %s" % (i, a, ia, b, ib, mark))
print("  命中 %d/11" % hits)

print("\n★★ 反向：正确字在 2838 表 idx vs 乱码字在 2795 表 idx")
hits2 = 0
for i, (a, b) in enumerate(zip(COR, GAR)):
    ia = c2i2838.get(a)
    ib = c2i2795.get(b)
    mark = "★★★ 相同!" if ia == ib else ""
    if ia == ib: hits2 += 1
    print("  %2d %r 2838idx=%-5s  |  %r 2795idx=%-5s  %s" % (i, a, ia, b, ib, mark))
print("  命中 %d/11" % hits2)

# 另一种：乱码字在 2795 表的 idx 是否等于 正确字在 2795 表的 idx + 常数
print("\n★ 两表差异（同 idx 处码点不同）的前几个位置")
print("  idx  2795表  2838表")
for i in range(220, 250):
    a = chr(CL2795[i]) if i < len(CL2795) else '-'
    b = chr(J2838[i]) if i < len(J2838) else '-'
    flag = "  <-- 不同" if a != b else ""
    print("  %3d   %r      %r%s" % (i, a, b, flag))
