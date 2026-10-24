# -*- coding: utf-8 -*-
"""★★★ 用真机 static_CH 的原始 slot + 三种表，看哪种能渲染出正确字幕

真机事实（截图）：
  字幕 = 任璨偶巧位雄衡任璨伪该
  HUD  = 正确中文

static_CH 里 REC1 的 slot（大端 u16）= [403,1868,59,70,79,82,77,65,84,61,59,67,79,76,79,82,26,71,82,69,69,78,61,1035,422,332,59,15,70,79,82,77,65,84,61,2667,2296,371,1836,391,1190] （idx=slot-0x20）

★ 若用【2795 表 + slot】解: 你的[format][color:green]弟兄们[/format]需要你的保护  ✓
★ 但真机显示乱码!

⇒ 关键：真机用的不是这个表！
   猜测：引擎用了【2838 的官方表】去解 2795 编码的 slot
"""
import sys, os, struct, json, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL2795 = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
          if s.strip().isdigit()]
J2838 = json.load(open(r"F:\sr2-cn\_day_2026-10-07\04_规则与数据\_expected_charlist.json"))

# REC1 slot（从 static_CH 用大端解出）
REC1_SLOTS = [403,1868,59,70,79,82,77,65,84,61,59,67,79,76,79,82,26,71,82,69,69,78,61,1035,422,332,59,15,70,79,82,77,65,84,61,2667,2296,371,1836,391,1190]

def decode(slots, table, off):
    out = []
    for s in slots:
        j = s - off
        if 0 <= j < len(table):
            out.append(chr(table[j]))
        else:
            out.append('?')
    return ''.join(out)

print("REC1 slot 序列（idx = slot-0x20）:")
print(" ", [s for s in REC1_SLOTS])

print("\nA) 2795 表, idx = slot-0x20 :")
print("  ", decode(REC1_SLOTS, CL2795, 0x20))
print("\nB) 2838 表, idx = slot-0x20 :")
print("  ", decode(REC1_SLOTS, J2838, 0x20))
print("\nC) 2795 表, idx = slot      :")
print("  ", decode(REC1_SLOTS, CL2795, 0))
print("\nD) 2838 表, idx = slot      :")
print("  ", decode(REC1_SLOTS, J2838, 0))

# 真机看到: 任璨偶巧位雄衡任璨伪该
print("\n真机看到: 任璨偶巧位雄衡任璨伪该")

# 暴力求解：在 2838 表里，哪个偏移能把 idx 映射成乱码字？
print("\n★ 暴力：找 2838 表里使 你(4F60) 的 slot 解出 任(4EFB) 的偏移")
for target_ch, ch_name in (('任', '你'), ('璨', '的'), ('偶', '弟'), ('位', '们')):
    tc = ord(target_ch)
    for i, cp in enumerate(J2838):
        if cp == tc:
            print("   2838[%d] = %r  (要解出'%r'，slot 应为 %d)" % (i, target_ch, ch_name, i+0x20))
