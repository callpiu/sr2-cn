# -*- coding: utf-8 -*-
"""★★★ 突破：ASCII 用 idx=slot（正确），CJK 用 idx=slot 得到乱码

Option C 结果: 值督[format][color:green]弟兄们[/format]需要你的保护
              ^^^^                                ^^^^^^^^^^^^^^
              CJK出错                              ★ CJK 对了!!

等等 —— 仔细看：
  '你'(slot 403) -> '值'   ✗
  '的'(slot 1868) -> '督'  ✗
  '[format]' 等 ASCII 全对 ✓
  '弟'(slot 1035) -> '弟'  ✓ !!
  '兄'(slot 422) -> '兄'  ✓ !!
  '们'(slot 332) -> '们'  ✓ !!
  '需'(slot 2667) -> '需'  ✓ !!
  '要'(slot 2296) -> '要'  ✓ !!
  '你'(slot 403) -> '你'   ✓ !!
  '保'(slot 391) -> '保'   ✓ !!
  '护'(slot 1190) -> '护'  ✓ !!

★ 只有 slot 403 和 1868 错了（前两个字 "你的"）！

⇒ 这说明: 同一个 slot 出现在不同位置时解析不同？
  不可能。一定是【前两个 slot 被另一个机制改写了】
  或者是 "你的" 这两个字走了不同的 slot 编码。
"""
import sys, os, struct, json
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]

REC1 = [403,1868,59,70,79,82,77,65,84,61,59,67,79,76,79,82,26,71,82,69,69,78,61,1035,422,332,59,15,70,79,82,77,65,84,61,2667,2296,371,1836,391,1190]

print("逐 slot 用 idx=slot 解 2795 表：")
for i, s in enumerate(REC1):
    ch = chr(CL[s]) if s < len(CL) else '?'
    print("  %2d slot=%-5d -> %r" % (i, s, ch))

print("\n★ 注意位置 24,25,26 是 slot 422,332,59")
print("   位置 2 也是 slot 59 ->", repr(chr(CL[59])))
print("   位置 10 也是 slot 59 ->", repr(chr(CL[59])))
