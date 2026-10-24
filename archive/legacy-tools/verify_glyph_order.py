# -*- coding: utf-8 -*-
"""决定性验证：字体字形表的真实顺序。

已知
    内存里字幕槽位 = [437, 994, 390, ...]
    charlist_CH[437] = 兄      （验证过）
    charlist_CH[994] = 弟
    charlist_CH[390] = 們
    屏幕显示        = 使 發 光      ← 不对！

    引擎文档说: 槽位 = charlist_index + 0x20
    如果引擎在【渲染时】把 charlist index 当成字形索引（漏掉 +0x20）：
        字形索引 = 437 - 0x20 = 405
        charlist_CH[405] = ?     ← 就是这个字应该在屏幕上

矛盾
    如果字形表顺序 == charlist_CH 顺序，那应该显示 charlist_CH[405]
    但屏幕显示的是别的字 -> 说明字形表顺序 != charlist_CH 顺序

本脚本
    1. 检查 charlist_CH[437-0x20] = charlist_CH[405] 是什么字
    2. 检查屏幕显示的「使」在 charlist_CH 里的索引
    3. 寻找「字形表顺序」的候选公式
"""
import os
import sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

with LightVpp(os.path.join(G, "patch.vpp_pc")) as v:
    for e in v.entries():
        if v.name(e) == "charlist_CH":
            cn = [int(l) for l in v.read(e).decode("utf-8", "replace").split("\n")
                  if l.strip().isdigit()]
            break

S = {i: chr(cp) for i, cp in enumerate(cn)}
IDX = {chr(cp): i for i, cp in enumerate(cn)}

print("charlist_CH: %d 项" % len(cn))
print()

# 我们的字幕
SLOTS = [437, 994, 390, 1488, 2311, 562]
EXPECT = "兄弟們正要去"
SHOWN = "使發光彈借步"

print("=" * 76)
print("1. 基本对照")
print("=" * 76)
print("  %-6s %-8s %-10s %-10s %-10s %s" %
      ("槽位", "-0x20", "charlist[槽位]", "charlist[槽位-0x20]", "屏幕显示", "屏幕字索引"))
for i, s in enumerate(SLOTS):
    c1 = S.get(s, "?")
    c2 = S.get(s - 0x20, "?")
    sh = SHOWN[i] if i < len(SHOWN) else "?"
    print("  %-6d %-8d %-10s %-10s %-10s %d" %
          (s, s - 0x20, c1, c2, sh, IDX.get(sh, -1)))
print()

print("=" * 76)
print("2. 检验：屏幕字 == charlist_CH[槽位 - 0x20] ?")
print("=" * 76)
hit = 0
for i, s in enumerate(SLOTS):
    c2 = S.get(s - 0x20, "?")
    sh = SHOWN[i]
    ok = c2 == sh
    if ok:
        hit += 1
    print("  槽位 %-5d -> charlist[%-5d] = %-4s   屏幕 = %-4s  %s" %
          (s, s - 0x20, c2, sh, "✓" if ok else "✗"))
print("  命中 %d/%d" % (hit, len(SLOTS)))
print()

print("=" * 76)
print("3. 检验：屏幕字 == charlist_CH[槽位] ?")
print("=" * 76)
hit = 0
for i, s in enumerate(SLOTS):
    c1 = S.get(s, "?")
    sh = SHOWN[i]
    ok = c1 == sh
    if ok:
        hit += 1
    print("  槽位 %-5d -> charlist[%-5d] = %-4s   屏幕 = %-4s  %s" %
          (s, s, c1, sh, "✓" if ok else "✗"))
print("  命中 %d/%d" % (hit, len(SLOTS)))
print()

print("=" * 76)
print("4. 关键：期望字「兄」在 charlist 里的索引 vs 槽位")
print("=" * 76)
for i, s in enumerate(SLOTS):
    exp = EXPECT[i] if i < len(EXPECT) else "?"
    sh = SHOWN[i]
    ei = IDX.get(exp, -1)
    si = IDX.get(sh, -1)
    print("  槽位 %-5d  期望 %s (idx %-5d)  屏幕 %s (idx %-5d)  差 %+d" %
          (s, exp, ei, sh, si, si - ei))
print()
print("  ★ 如果「屏幕字索引」有规律，就能反推出字形表顺序")
print()
print("  屏幕字索引: %s" % [IDX.get(SHOWN[i], -1) for i in range(len(SHOWN))])
print("  期望字索引: %s" % [IDX.get(EXPECT[i], -1) for i in range(len(EXPECT))])
print("  槽位:       %s" % SLOTS)
print("  槽位-0x20:  %s" % [s - 0x20 for s in SLOTS])
