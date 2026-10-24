# -*- coding: utf-8 -*-
"""★ 检验：是否 正确字.slot  ->  乱码字.idx = 正确字.slot - 0x20 - 0x20 ?
   即 乱码字的 charlist 索引 = 正确字的 charlist 索引 - 32 ?

   注意 '你'→'伪' 是因为我 GARBLE 串里的第8字是'伪'，而 CORRECT 第8字是'你'。
   真正的映射是逐字节位的，先只看有意义的组合。
"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]
c2i = {}
for i, cp in enumerate(CL):
    c2i.setdefault(chr(cp), i)

# 真机记忆里捕获的乱码串（scan3）：任璨偶巧位
MEM_GARBLE = "任璨偶巧位"
# 对应位置正确的字
CORRECT_HEAD = "你的弟兄们"

print("== 假设 H-A: 乱码字.idx == 正确字.idx - 32 ==")
ok = 0
for a, b in zip(CORRECT_HEAD, MEM_GARBLE):
    ia, ib = c2i.get(a), c2i.get(b)
    pred = ia - 32
    hit = (pred == ib)
    ok += hit
    print("   %r idx=%-5d  -32 = %-5d   乱码 %r idx=%-5d   %s" % (a, ia, pred, b, ib, "✓" if hit else "✗"))
print("  命中 %d/5" % ok)

print("\n== 假设 H-B: 乱码字.idx == 正确字.idx - 31 ==")
for d in range(-40, 41):
    n = sum(1 for a, b in zip(CORRECT_HEAD, MEM_GARBLE) if c2i.get(b) == c2i.get(a, 0) + d)
    if n >= 2:
        print("   delta=%+d 命中 %d/5" % (d, n))

print("\n== 假设 H-C: 用 slot 而非 idx ==")
s2i = {}
for i, cp in enumerate(CL):
    s2i.setdefault(chr(cp), i + 0x20)
for d in range(-40, 41):
    n = sum(1 for a, b in zip(CORRECT_HEAD, MEM_GARBLE) if c2i.get(b) == s2i.get(a, 0) + d)
    if n >= 2:
        print("   slot 上的 delta=%+d 命中 %d/5" % (d, n))

print("\n== 直接验证：乱码字在 charlist 里的索引 是否 = 正确字在图集分块中的位置 ==")
# 思路：引擎可能把 slot 当作 官方图集的 vf3 索引，得到的是【字形】，然后按【字形在
# 汉化 charlist 中匹配】反查 -> 但引擎不认识字形。所以更可能：
# 引擎用 slot 作为 common vf3(2838) 的索引，得到 U/V 坐标，在【官方图集】上取图。
# 那个图中的字 = ？
# 我们需要：官方图集里 idx 位置的字形是什么字？= common charlist(2838) 的第 idx 项
import json, glob
p = r"F:\sr2-cn\_day_2026-10-07\04_规则与数据\_expected_charlist.json"
if os.path.exists(p):
    J = json.load(open(p))
    print("   JSON 2838 表长度 =", len(J))
    for a, b in zip(CORRECT_HEAD, MEM_GARBLE):
        sl = s2i.get(a)
        got = chr(J[sl]) if sl and sl < len(J) else None
        print("   %r slot=%-5d -> JSON[slot]=%r   期望乱码=%r  %s" % (a, sl, got, b, "✓" if got == b else "✗"))
