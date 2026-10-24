# -*- coding: utf-8 -*-
"""识别字幕用的「真实字形表」。

现象
    同一个槽位索引 358 在 REC2 里出现两次：
        位置 2  -> 屏幕显示「光」
        位置 14 -> 屏幕显示「誘」
    => 屏幕显示【不是】槽位索引的单一函数 => 不是简单的「表A换表B」

这说明：字幕的渲染是【位置相关】的，很可能是：
    (a) 字幕文本被逐字做了某种变换（如按位置增量取模）
    (b) 或者用户抄录有误（截图 OCR 由人眼完成）

本脚本
    列出所有已知数据，并把「槽位 -> 屏幕」的映射整理成表，
    同时检查是否存在【位置相关】的简单公式。
"""
import os, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SLOTS = [437, 994, 390, 1488, 2311, 562, 2534, 2275, 319, 1322,
         2862, 382, 2385, 331, 390, 2556, 444, 570, 486, 1274, 1252]
EXPECT = "兄弟們正要去進行交易，保護他們避免受到攻擊"
GARBLED = "使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋"

with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    for e in pv.entries():
        if pv.name(e) == "charlist_CH":
            cn = [int(l) for l in pv.read(e).decode("utf-8", "replace").split("\n") if l.strip().isdigit()]
            break

print("=" * 78)
print("A. 槽位的真实值 vs 期望字")
print("=" * 78)
for i, s in enumerate(SLOTS):
    exp = EXPECT[i] if i < len(EXPECT) else "?"
    print("  %-3d 槽位 %-6d (idx %-6d) 期望 %s" % (i, s, s - 0x20, exp))
print()

print("=" * 78)
print("B. 屏幕字 vs 它在 charlist_CH 的索引")
print("=" * 78)
IDX = {chr(cp): i for i, cp in enumerate(cn)}
for i, g in enumerate(GARBLED):
    print("  %-3d 屏幕 %s  索引 %d" % (i, g, IDX.get(g, -1)))
print()

print("=" * 78)
print("C. 关键检验：同一槽位是否出现两次 -> 屏幕是否相同")
print("=" * 78)
seen = {}
for i, s in enumerate(SLOTS):
    g = GARBLED[i] if i < len(GARBLED) else "?"
    if s in seen:
        print("  槽位 %d 出现两次: 位置 %d -> %s, 位置 %d -> %s  %s" %
              (s, seen[s][0], seen[s][1], i, g, "✓ 一致" if seen[s][1] == g else "✗ 不一致！"))
    else:
        seen[s] = (i, g)
print()

print("=" * 78)
print("D. 检验：屏幕索引 是否是 期望索引 的某种「位运算」")
print("=" * 78)
diffs = []
for i, s in enumerate(SLOTS):
    si = s - 0x20
    gi = IDX.get(GARBLED[i], -1)
    diffs.append(gi - si)
    print("  %-3d %-4s idx %-6d -> %-4s idx %-6d  差 %-+7d  XOR %-6d  AND-FF %-4d" %
          (i, EXPECT[i], si, GARBLED[i], gi, gi - si, si ^ gi, gi & 0xFF))
print()
print("  差值序列: %s" % diffs)
print("  差值是否随位置单调? %s" % ("是" if all(diffs[i] <= diffs[i+1] for i in range(len(diffs)-1)) else "否"))
print()

print("=" * 78)
print("E. 是否可能是「字体图集格号」= slot - 0x20 + 某偏移，再按图集列数取模")
print("=" * 78)
# 汉化图集：65 列，步距 31（交接文档 §2.1）
for COLS in (64, 65, 66, 67, 68, 70, 72, 80):
    hit = 0
    for i, s in enumerate(SLOTS):
        si = s - 0x20
        gi = IDX.get(GARBLED[i], -1)
        if gi < 0:
            continue
        # 尝试 gi = 某个重排：行/列互换
        r1, c1 = divmod(si, COLS)
        r2, c2 = divmod(gi, COLS)
        if c1 == c2:
            hit += 1
    print("  列数 %-3d  列相同的位置数 %d / %d" % (COLS, hit, len(SLOTS)))
