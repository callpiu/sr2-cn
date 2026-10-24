# -*- coding: utf-8 -*-
"""精确求解：槽位索引 -> 屏幕字形索引 的映射。

精确数据（繁中 patch.vpp_pc, static_CH）
    REC1 (0x84F287ED, 9 个 CJK):
        槽位      437  994  390  2704  2311  365  1819  382  2385
        期望字    兄   弟   們   需    要    你   的    保   護
    REC2 (0x10AF1E62, 21 个 CJK):
        槽位      437  994  390  1488  2311  562  2534  2275  319  1322
                  2862  382  2385  331   390   2556  444   570  486  1274  1252
        期望字    兄   弟   們   正    要    去   進    行   交   易
                  ，   保   護   他    們    避   免    受   到   攻   擊

    用户看到（REC2 那一行，22 字）:
        使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋

任务
    求 槽位 -> 屏幕字 的映射，检查是否为某个已知字符串的重排。
"""
import os, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 精确槽位
REC2_SLOTS = [437, 994, 390, 1488, 2311, 562, 2534, 2275, 319, 1322,
              2862, 382, 2385, 331, 390, 2556, 444, 570, 486, 1274, 1252]
REC2_EXPECT = "兄弟們正要去進行交易，保護他們避免受到攻擊"
GARBLED = "使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋"

with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    for e in pv.entries():
        if pv.name(e) == "charlist_CH":
            cn = [int(l) for l in pv.read(e).decode("utf-8", "replace").split("\n") if l.strip().isdigit()]
            break

print("charlist_CH %d 项" % len(cn))
IDX = {chr(cp): i for i, cp in enumerate(cn)}

# 建立 槽位 -> 屏幕字
print()
print("=== 槽位 -> 屏幕字（按用户报告对齐）===")
print("  %-4s %-8s %-8s %-8s %-10s %s" % ("位", "槽位", "槽位-0x20", "期望字", "屏幕字", "屏幕字索引"))
pairs = []
for i, s in enumerate(REC2_SLOTS):
    exp = REC2_EXPECT[i] if i < len(REC2_EXPECT) else "?"
    gar = GARBLED[i] if i < len(GARBLED) else "?"
    gi = IDX.get(gar, -1)
    pairs.append((s, s - 0x20, exp, gar, gi))
    print("  %-4d %-8d %-8d %-8s %-10s %d" % (i, s, s - 0x20, exp, gar, gi))
print()

print("=== 检查：屏幕字索引 是否 = 槽位 在【另一套表】的值 ===")
# 读所有可用字符表
tables = {}
for fn in ("patch.vpp_pc", "common.vpp_pc"):
    try:
        with LightVpp(os.path.join(G, fn)) as v:
            for e in v.entries():
                nm = v.name(e)
                if nm.startswith("charlist_"):
                    tables["%s/%s" % (fn[:6], nm)] = [
                        int(l) for l in v.read(e).decode("utf-8", "replace").split("\n") if l.strip().isdigit()]
    except Exception as ex:
        print("  %s: %s" % (fn, ex))
print("  找到 %d 套表" % len(tables))
for k in sorted(tables):
    print("    %-28s %d 项" % (k, len(tables[k])))
print()

# 关键检验：把「屏幕字的索引」拿去各表查，看是否有规律
print("=== 屏幕字索引 与 槽位索引 的比值/差值 ===")
for i, (s, si, exp, gar, gi) in enumerate(pairs):
    if gi < 0:
        continue
    print("  %-4d %-8s 槽位idx=%-6d 屏幕idx=%-6d 差=%-+7d 比=%.4f" %
          (i, gar, si, gi, gi - si, gi / si if si else 0))
print()

# 最终检验：屏幕字是否就是「槽位值」在 charlist_CH 里的字（即多加了 0x20）
print("=== 检验：屏幕字 == charlist_CH[槽位值] ===")
hit = 0
for i, s in enumerate(REC2_SLOTS):
    ch = chr(cn[s]) if 0 <= s < len(cn) else "?"
    exp_gar = GARBLED[i] if i < len(GARBLED) else "?"
    ok = ch == exp_gar
    if ok:
        hit += 1
    print("  %-4d 槽位=%-6d cn[%d]=%-4s 用户看到=%-4s %s" % (i, s, s, ch, exp_gar, "✓" if ok else "✗"))
print("  命中 %d/%d" % (hit, len(REC2_SLOTS)))
