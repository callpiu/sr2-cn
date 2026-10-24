# -*- coding: utf-8 -*-
"""★ 从两张真机截图提取的乱码，反推映射

截图1 字幕: 任璨 偶巧位 雄衡任璨伪该
截图2 字幕: 任璨 偶巧位 校衡勾远藐乱携，伪该亡位通像匪冰挺拮

正确文本1: 你的 弟兄们 需要你的保护        (11 字)
正确文本2: 你的 弟兄们 要出去谈几笔生意，保护他们免遭袭击   (含 [format] 标签)

关键：HUD 中文(直升机突击/已完成停靠/面包车耐久/迷雾巷)【正常】
     字幕【乱码】—— 同一字体，不同文本来源！
     => 问题不在字体/图集，而在【字幕的 slot 序列】本身错位。
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]
print("charlist_CH =", len(CL))
# 建立 码点->索引
c2i = {}
for i, cp in enumerate(CL):
    c2i.setdefault(chr(cp), i)

# 真机看到的乱码
SC1 = "任璨偶巧位雄衡任璨伪该"
SC2 = "任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮"

COR1 = "你的弟兄们需要你的保护"
COR2 = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"

print("\n=== 截图1 逐字 ===")
print("正确:", COR1, len(COR1))
print("乱码:", SC1, len(SC1))
for i, (a, b) in enumerate(zip(COR1, SC1)):
    ia, ib = c2i.get(a), c2i.get(b)
    print("  %2d %r(idx=%-5s) -> %r(idx=%-5s)  d=%s" % (
        i, a, ia, b, ib, (ib - ia) if (ia is not None and ib is not None) else "?"))

print("\n=== 截图2 逐字 ===")
print("正确:", COR2, len(COR2))
print("乱码:", SC2, len(SC2))

# 关键洞察检验：HUD 正常 => patch 字体被正确使用
# 那字幕的乱码字在 charlist 中的索引 vs 正确字的索引
print("\n★ 检查：乱码字本身在 charlist_CH 里的索引")
for ch in set(SC1 + SC2):
    if ch not in '，':
        print("   %r idx=%s" % (ch, c2i.get(ch)))
