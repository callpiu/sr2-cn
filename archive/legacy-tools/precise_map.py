# -*- coding: utf-8 -*-
"""精确计算：槽位 -> 乱码字 的索引映射。

数据（繁中 patch.vpp_pc，static_CH hash 0x10AF1E62）
    槽位: 见下方 SLOTS
    用户截图乱码: 使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋
"""
import os, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SLOTS = [437, 994, 390, 1488, 2311, 562, 2534, 2275, 319, 1322,
         2862, 382, 2385, 331, 390, 2556, 444, 570, 486, 1274, 1252]
GARBLED = "使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋"

with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    for e in pv.entries():
        if pv.name(e) == "charlist_CH":
            cn = [int(l) for l in pv.read(e).decode("utf-8", "replace").split("\n") if l.strip().isdigit()]
            break

print("charlist_CH: %d 项" % len(cn))
print()
print("槽位对应的【期望字】:")
print("  " + "".join(chr(cn[s - 0x20]) for s in SLOTS))
print()
print("用户看到的乱码 (%d 字):" % len(GARBLED))
print("  " + GARBLED)
print()

# 精确计算乱码字的索引
IDX = {chr(cp): i for i, cp in enumerate(cn)}
print("=== 精确索引对照 ===")
print("  %-4s %-8s %-8s %-8s %-10s %s" % ("位", "槽位", "槽位-0x20", "期望索引", "乱码字", "乱码索引"))
rows = []
for i, s in enumerate(SLOTS):
    gar = GARBLED[i] if i < len(GARBLED) else "?"
    gi = IDX.get(gar, -1)
    rows.append((s, s - 0x20, gi, gar))
    print("  %-4d %-8d %-8d %-8d %-10s %d" % (i, s, s - 0x20, s - 0x20, gar, gi))
print()

print("=== 关系分析 ===")
print("  %-4s %-10s %-10s %-12s %s" % ("位", "槽位-0x20", "乱码索引", "差(乱码-slot)", "乱码*? / 槽位"))
for i, (s, si, gi, gar) in enumerate(rows):
    d = gi - si
    ratio = (gi / si) if si else 0
    print("  %-4d %-10d %-10d %+12d   %.4f" % (i, si, gi, d, ratio))
print()

# 检验：乱码索引 是否 = 槽位索引 在【另一套字表】里的对应
print("=== 检验：槽位索引在其它字表里是什么字 ===")
with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    tabs = {}
    for e in pv.entries():
        nm = pv.name(e)
        if nm.startswith("charlist_"):
            tabs[nm] = [int(l) for l in pv.read(e).decode("utf-8", "replace").split("\n") if l.strip().isdigit()]
for nm, cps in sorted(tabs.items()):
    out = []
    for s, si, gi, gar in rows:
        out.append(chr(cps[si]) if 0 <= si < len(cps) else "?")
    hit = sum(1 for a, b in zip(out, GARBLED) if a == b)
    print("  %-16s %s  命中 %d/%d" % (nm, "".join(out), hit, len(GARBLED)))
