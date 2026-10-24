"""v417 审计：static_CH 中 %ls 与 %d/%i 混用的记录，用占位符【顺序】与 static_US 配对。

崩溃机制回顾：引擎按 US 字符串的占位符顺序传参，若 CH 顺序与 US 不同，
则 %ls 会把整数当字符串指针 → strlen16(0x1) 崩溃（拆车厂即此例）。

本脚本精确比对【顺序】，而非仅多重集，避免漏判/误判。
"""
import sys, os, re, collections
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units, SHIFT

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(GAME, "patch.vpp_pc")

v = Vpp(SRC)
e_cl = v.find("charlist_CH", "txt")
nums = [int(x) for x in v.read(e_cl).decode('utf-8', 'replace').split()
        if x.strip().lstrip('-').isdigit()]
cl = nums[1:] if nums and nums[0] == len(nums) - 1 else nums
S = {i + SHIFT: chr(c) for i, c in enumerate(cl)}


def table(name):
    ent = v.find(name, "le_strings")
    d = v.read(ent)
    b, c, oa, offs = file_offsets(d)
    n = len(d)
    recs = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= n - 24):
            continue
        u, end = read_units(d, off + 8)
        if u is None:
            continue
        t = "".join(chr(vv) if vv < 0x100 else S.get(vv, '\ufffd') for vv, _ in u)
        recs.append((off, t))
    return recs


def specseq(t):
    return re.findall(r'%l[si]|%[diufcs]', t)


us = table("static_US")
us_by_order = collections.defaultdict(list)
us_by_multi = collections.defaultdict(list)
for off, t in us:
    sp = specseq(t)
    if '%ls' in sp and ('%d' in sp or '%i' in sp):
        us_by_order[tuple(sp)].append((off, t))
        us_by_multi[tuple(sorted(sp))].append((off, t))

ch = table("static_CH")
print("== CH 混合占位符记录：顺序 vs US 检查（基于当前游戏目录 %s）==" % os.path.basename(SRC))
risky = []
for off, t in ch:
    sp = specseq(t)
    if '%ls' in sp and ('%d' in sp or '%i' in sp):
        order = tuple(sp)
        multi = tuple(sorted(sp))
        if us_by_order.get(order):
            verdict = "OK（与 US 某条顺序完全一致）"
        else:
            cand = us_by_multi.get(multi, [])
            verdict = "★ 顺序与所有 US 候选不同→疑似隐患"
            risky.append((off, t, order, [(co, ct) for co, ct in cand[:3]]))
        print("  @0x%-6X %-22s %r\n        %s" % (off, str(order), t, verdict))
        if risky and risky[-1][0] == off:
            for co, ct in risky[-1][3]:
                print("          US候选 @0x%-6X %s" % (co, ct))
print()
print("疑似隐患条数: %d" % len(risky))
for off, t, order, cand in risky:
    print("  @0x%-6X %s %r" % (off, order, t))
