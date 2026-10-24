# -*- coding: utf-8 -*-
"""反查：这次的字幕乱码是用哪套字符表解码出来的？

已知
    static_CH (hash 0x10AF1E62) 槽位 = 
      [91,102,111,114,109,97,116,93, 91,99,111,108,111,114,58,103,114,101,101,110,93,
       1067,454,364, 91,47,102,111,114,109,97,116,93, 2328,510,613,2389,502,1995,1824,1159,2822,423,1222,356,364,460,2563,2312,511]
    中文（用 charlist_CH 2838 项） = 你的[format][color:green]兄弟們[/format]正要去進行交易，保護他們避免受到攻擊

用户新截图看到的乱码 = 使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋

任务
    遍历所有可能的字符表，找哪个能把槽位解成乱码字。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
GARBLED = "使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋"
print("乱码 %d 字: %s" % (len(GARBLED), GARBLED))
print()

# 读 static_CH 的槽位
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

v = Vpp(os.path.join(G, "patch.vpp_pc"))
d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)
H2 = 0x10AF1E62
slots = None
for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
    id1, id2 = struct.unpack_from("<HH", d, off)
    if ((id1 << 16) | id2) == H2:
        u, _ = read_units(d, off + 8)
        slots = [x for x, _ in u]
        break
print("static_CH 0x%08X 槽位 (%d 个):" % (H2, len(slots)))
print("  %s" % slots)
print()

# 收集所有字符表
tables = {}
with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    for e in pv.entries():
        nm = pv.name(e)
        if nm.startswith("charlist_"):
            raw = pv.read(e).decode("utf-8", "replace")
            cps = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
            tables["patch/" + nm] = cps
with LightVpp(os.path.join(G, "common.vpp_pc")) as cv:
    for e in cv.entries():
        nm = cv.name(e)
        if nm.startswith("charlist_"):
            raw = cv.read(e).decode("utf-8", "replace")
            cps = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
            tables["common/" + nm] = cps

for k in sorted(tables):
    print("  字符表 %-24s %d 项" % (k, len(tables[k])))
print()

# 逐个尝试
print("=== 用各字符表解码槽位 ===")
for k, cps in sorted(tables.items()):
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cps)}
    t = "".join(S.get(x, "·") for x in slots)
    hit = sum(1 for a, b in zip(GARBLED, [c for c in t if ord(c) > 0x2000]) if a == b)
    mark = "  <<< 完全匹配!" if t.replace("·", "") == GARBLED else ""
    print("  %-24s %s%s" % (k, t[:64], mark))
print()

# 精确匹配尝试：乱码字在各表里的索引
print("=== 乱码字在各字符表里的索引 ===")
for k, cps in sorted(tables.items()):
    IDX = {chr(cp): i for i, cp in enumerate(cps)}
    idxs = [IDX.get(ch, -1) for ch in GARBLED]
    print("  %-24s %s" % (k, idxs))
print()
print("=== 槽位里的 CJK 部分（应为 兄弟們... ）===")
cjk_slots = [x for x in slots if x > 0x100]
print("  %s" % cjk_slots)
print("  乱码字的可能索引 = 槽位-0x20 = %s" % [x - 0x20 for x in cjk_slots])
