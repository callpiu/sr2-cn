# -*- coding: utf-8 -*-
"""验证「M = 原版繁中 charlist 索引」假说，并给出完整修复方案。

假说
    引擎用【原版繁中 charlist 的索引】去查图集。
    简体补丁替换了 charlist_CH（改成简体顺序），导致索引错位。

验证
    对每对 (原字 c, 显示字 d)：
        clist_va.index(c) - OFFSET  应等于  clist_cn.index(d) - OFFSET
    即两者索引应相等（或差一个常数）

修复思路
    把 charlist_CH 改成「原版繁中顺序」：
        新表[j] = 原版 charlist[j]   （对 j < 2838）
    这样引擎按繁中索引查表，得到的仍是原版字符 -> 图集位置正确。
"""
import re
import sys
import json

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp

OFFSET = 5
VANILLA = r"F:\sr2-cn\pristine\patch.vpp_pc"
CN = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"


def load_cl(p):
    v = Vpp(p)
    raw = v.read(v.find("charlist_CH", "txt"))
    m = re.search(rb"count\s*=\s*(\d+)", raw)
    body = raw[m.end():] if m else raw
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


cl_va = load_cl(VANILLA)
cl_cn = load_cl(CN)
IVA = {cp: i for i, cp in enumerate(cl_va)}
ICN = {cp: i for i, cp in enumerate(cl_cn)}

cfg = json.load(open(r"F:\sr2-cn\pairs_cn.json", encoding="utf-8"))

print("=" * 86)
print("验证：clist_va.index(原字) 与 clist_cn.index(显示字) 的关系")
print("=" * 86)
print("  %-4s %-8s %-4s %-8s %-8s %s" % ("原字", "va_idx", "显示", "cn_idx", "差值", "判定"))
deltas = {}
for c, d in cfg["pairs"]:
    oc, od = ord(c), ord(d)
    iva = IVA.get(oc)
    icn = ICN.get(od)
    if iva is None or icn is None:
        print("  %-4s %-8s %-4s %-8s (缺)" % (c, iva if iva is not None else "-", d, icn if icn is not None else "-"))
        continue
    delta = icn - iva
    deltas[delta] = deltas.get(delta, 0) + 1
    print("  %-4s %-8d %-4s %-8d %-8d %s" % (c, iva, d, icn, delta, "(同一索引且差0)" if delta == 0 else ""))
print()
print("  差值分布: %s" % dict(sorted(deltas.items())))
print()

# 换一个更强的检验：显示字 d 在简体表里的索引，是否对应原版表里的「原字 c」？
# 即 cl_cn[iva] 是什么字？
print("=" * 86)
print("强检验：cl_cn[ clist_va.index(原字) ] == 显示字 ?")
print("=" * 86)
hit = 0
tot = 0
for c, d in cfg["pairs"]:
    oc, od = ord(c), ord(d)
    iva = IVA.get(oc)
    if iva is None or iva >= len(cl_cn):
        continue
    tot += 1
    got = cl_cn[iva]
    ok = (got == od)
    if ok:
        hit += 1
    print("  原字 %-3s (va_idx %-5d) -> cl_cn[%d] = %-3s   显示字 = %-3s  %s" %
          (c, iva, iva, chr(got), d, "✓" if ok else "✗"))
print()
print("  ★ 命中 %d/%d" % (hit, tot))
print()

# 另一个检验：字节层面 —— 简体表的第 i 项，其【原版对应项】是什么
print("=" * 86)
print("检验：简体表的每一项，是否等于「原版同位置的繁体字」的简体形？")
print("=" * 86)
same = 0
diff = 0
for i in range(min(len(cl_va), len(cl_cn))):
    if cl_va[i] == cl_cn[i]:
        same += 1
    else:
        diff += 1
print("  前 %d 项中，相同 %d 项，不同 %d 项" % (min(len(cl_va), len(cl_cn)), same, diff))
print("  前 30 项的对照（原版 vs 简体）:")
for i in range(min(30, len(cl_va), len(cl_cn))):
    mark = "" if cl_va[i] == cl_cn[i] else "  ← 不同"
    print("    [%-4d] 原版 %s (U+%04X)   简体 %s (U+%04X)%s" %
          (i, chr(cl_va[i]), cl_va[i], chr(cl_cn[i]), cl_cn[i], mark))
