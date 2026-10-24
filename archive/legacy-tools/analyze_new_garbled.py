# -*- coding: utf-8 -*-
"""精确分析：新乱码字与槽位的关系。

数据
    static_CH 0x10AF1E62 的 CJK 槽位:
        437, 994, 390, 1488, 2311, 562, 2534, 2275, 319, 1322,
        2862, 382, 2385, 331, 390, 2556, 444, 570, 486, 1274, 1252
    用 charlist_CH (2838) 解码 = 兄弟們正要去進行交易，保護他們避免受到攻擊

    用户截图看到的乱码:
        使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋

任务
    建立 槽位 -> 乱码字 的精确映射，并寻找规律。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 槽位（来自上一步的解析）
SLOTS = [437, 994, 390, 1488, 2311, 562, 2534, 2275, 319, 1322,
         2862, 382, 2385, 331, 390, 2556, 444, 570, 486, 1274, 1252]
EXPECT = "兄弟們正要去進行交易，保護他們避免受到攻擊"
GARBLED = "使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋"

print("槽位数 %d, 期望 %d 字, 乱码 %d 字" % (len(SLOTS), len(EXPECT), len(GARBLED)))
print()

# 读 charlist_CH
with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    for e in pv.entries():
        if pv.name(e) == "charlist_CH":
            raw = pv.read(e).decode("utf-8", "replace")
            cn = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
            break
print("charlist_CH: %d 项" % len(cn))
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
IDX = {chr(cp): i for i, cp in enumerate(cn)}
print()

print("=== 对照表 ===")
print("  %-4s %-8s %-8s %-8s %-8s %-8s" % ("位", "槽位", "槽位-0x20", "期望字", "期望索引", "乱码字"))
rows = []
for i in range(min(len(SLOTS), len(GARBLED))):
    sl = SLOTS[i]
    exp = EXPECT[i] if i < len(EXPECT) else "?"
    gar = GARBLED[i]
    ei = IDX.get(exp, -1)
    gi = IDX.get(gar, -1)
    rows.append((sl, ei, gi, exp, gar))
    print("  %-4d %-8d %-8d %-8s %-8d %-8s" % (i, sl, sl - 0x20, exp, ei, gar))
print()

print("=== 差值分析 ===")
print("  %-4s %-8s %-8s %-10s %-10s" % ("位", "期望idx", "乱码idx", "乱码-期望", "乱码-槽位"))
for i, (sl, ei, gi, exp, gar) in enumerate(rows):
    print("  %-4d %-8d %-8d %+10d %+10d" % (i, ei, gi, gi - ei, gi - (sl - 0x20)))
print()

# 关键检验：是否「乱码idx = 槽位 - 0x20」？
print("=== 检验「乱码索引 == 槽位 - 0x20」===")
hit = 0
for i, (sl, ei, gi, exp, gar) in enumerate(rows):
    want = sl - 0x20
    ok = (gi == want)
    if ok:
        hit += 1
    print("  %-4d %-8s 槽位-0x20=%-6d 乱码idx=%-6d %s" %
          (i, gar, want, gi, "✓" if ok else "✗"))
print("  命中 %d / %d" % (hit, len(rows)))
print()

# 检验：乱码字是否在另一套表里恰好是 槽位-0x20
print("=== 检验：乱码字在某表的索引 == 槽位-0x20 ===")
with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    for e in pv.entries():
        nm = pv.name(e)
        if not nm.startswith("charlist_"):
            continue
        raw = pv.read(e).decode("utf-8", "replace")
        cps = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
        I2 = {chr(cp): i for i, cp in enumerate(cps)}
        hit = 0
        detail = []
        for i, (sl, ei, gi, exp, gar) in enumerate(rows):
            k = I2.get(gar, -1)
            if k == sl - 0x20:
                hit += 1
            detail.append(k)
        print("  %-16s 索引=%s  命中 %d/%d" % (nm, detail[:10], hit, len(rows)))
