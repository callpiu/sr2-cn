# -*- coding: utf-8 -*-
"""决定性检验：M 是否 =「charlist 按码点排序」的映射？

模型
    屏幕显示的字 d 满足:  charlist.index(d) = M_index(c)
    即引擎对字符 c 取用的格 k = charlist.index(d) - OFFSET
    如果引擎的索引表 M 是「按码点排序的位置」，那么：
        k = rank(c) - OFFSET
    其中 rank(c) = c 在 charlist 按码点升序排序后的位置

    则显示字 d 应满足:  charlist.index(d) = rank(c)
"""
import re
import struct
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


def build_rank(cl):
    order = sorted(range(len(cl)), key=lambda i: cl[i])
    rank = {}
    for r, i in enumerate(order):
        rank[cl[i]] = r
    return rank, order


def test(label, vpp, pairfile):
    cl = load_cl(vpp)
    rank, order = build_rank(cl)
    IDX = {cp: i for i, cp in enumerate(cl)}
    cfg = json.load(open(pairfile, encoding="utf-8"))
    pairs = cfg["pairs"]

    print("=" * 80)
    print("%s  (charlist %d 项)" % (label, len(cl)))
    print("=" * 80)
    print("  %-4s %-7s %-7s %-9s %-9s %-9s %s" %
          ("字", "码点", "clist", "rank", "E实测格", "rank-OFF", "匹配"))
    hit = 0
    tot = 0
    for c, d in pairs:
        oc, od = ord(c), ord(d)
        ic = IDX.get(oc, -1)
        idd = IDX.get(od, -1)
        if ic < 0 or idd < 0:
            print("  %-4s %-7d %-7s %-9s %-9s %-9s (字不在表)" %
                  (c, oc, ic if ic >= 0 else "-", rank.get(oc, "-"),
                   idd - OFFSET if idd >= 0 else "-", (rank.get(oc, 0) - OFFSET)))
            continue
        tot += 1
        E_measured = idd - OFFSET
        pred = rank[oc] - OFFSET
        ok = (pred == E_measured)
        if ok:
            hit += 1
        print("  %-4s %-7d %-7d %-9d %-9d %-9d %s" %
              (c, oc, ic, rank[oc], E_measured, pred, "✓" if ok else "✗"))
    print("  ★ rank 模型命中 %d/%d" % (hit, tot))
    print()

    # 另一个模型：显示字 d 的 rank 是否等于 c 的 rank？
    print("  模型 B: rank(d) == rank(c) ?")
    hit2 = 0
    for c, d in pairs:
        oc, od = ord(c), ord(d)
        if oc in rank and od in rank:
            if rank[oc] == rank[od]:
                hit2 += 1
    print("     命中 %d/%d" % (hit2, tot))
    print()

    # 模型 C: 显示字 d 的 clist 索引 == c 的 clist 索引 + 5？
    print("  模型 C: clist.index(d) == clist.index(c) + 5 ?")
    hit3 = 0
    diffs = {}
    for c, d in pairs:
        oc, od = ord(c), ord(d)
        if oc in IDX and od in IDX:
            df = IDX[od] - IDX[oc]
            diffs[df] = diffs.get(df, 0) + 1
            if df == 5:
                hit3 += 1
    print("     命中 %d/%d" % (hit3, tot))
    print("     差值分布: %s" % dict(sorted(diffs.items())))
    print()


if __name__ == "__main__":
    test("官方原版（繁中）", VANILLA, r"F:\sr2-cn\pairs_vanilla.json")
    test("简体汉化版", CN, r"F:\sr2-cn\pairs_cn.json")
