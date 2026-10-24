# -*- coding: utf-8 -*-
"""验证规律：乱码字索引 = 槽位（而不是 槽位 - 0x20）？

即：引擎渲染字幕时，把【槽位值本身】当成字形索引，多加了 0x20。

数据
    槽位            : 437, 994, 390, 1488, 2311, ...
    期望字（索引=槽位-0x20）: 兄弟們正要去進行交易，保護他們避免受到攻擊
    乱码字          : 使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋
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
            raw = pv.read(e).decode("utf-8", "replace")
            cn = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
            break

print("=== 检验各种索引公式 ===")
formulas = {
    "槽位 - 0x20 (期望)": lambda s: s - 0x20,
    "槽位 (原值)":        lambda s: s,
    "槽位 + 0x20":        lambda s: s + 0x20,
    "槽位 - 0x40":        lambda s: s - 0x40,
}
IDX = {chr(cp): i for i, cp in enumerate(cn)}
for name, f in formulas.items():
    hit = 0
    detail = []
    for i, s in enumerate(SLOTS):
        k = f(s)
        ch = chr(cn[k]) if 0 <= k < len(cn) else "?"
        detail.append(ch)
        if i < len(GARBLED) and ch == GARBLED[i]:
            hit += 1
    print("  %-20s %s   命中 %d/%d" % (name, "".join(detail), hit, len(GARBLED)))
print()

print("=== 逐字验证「乱码索引 == 槽位」===")
print("  %-4s %-6s %-8s %-8s %-8s %s" % ("位", "槽位", "槽位字", "槽位+0x20字", "用户看到", "匹配"))
allok = True
for i, s in enumerate(SLOTS):
    exp = chr(cn[s - 0x20]) if 0 <= s - 0x20 < len(cn) else "?"
    k = s
    got = chr(cn[k]) if 0 <= k < len(cn) else "?"
    user = GARBLED[i] if i < len(GARBLED) else "?"
    ok = (got == user)
    if not ok:
        allok = False
    print("  %-4d %-6d %-8s %-8s %-8s %s" % (i, s, exp, got, user, "✓" if ok else "✗"))
print()
print("全部匹配: %s" % ("是 ✓✓✓" if allok else "否"))
