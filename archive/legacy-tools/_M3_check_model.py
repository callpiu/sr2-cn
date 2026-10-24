# -*- coding: utf-8 -*-
"""检验：引擎索引 E 是否等于「charlist 按码点重排」后的位置？

文档实测（原版繁中，pairs_vanilla.json）:
    你 -> 显示 使
    的 -> 显示 發
    兄 -> 显示 光
    弟 -> 显示 彈
    ...

推导
    图集格 k 装的字 = charlist[k+5]        （已用图集视觉验证 ✓）
    屏幕显示 d  =>  引擎取的格 k = charlist.index(d) - 5
    所以 E(你) = charlist.index(使) - 5

    如果 E(c) =「c 在按码点排序的 charlist 里的位置」
    那么 E(你) 应该能直接算出来，并与实测吻合。
"""
import re
import struct
import sys
import os

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp

OFFSET = 5

CN = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"          # 简体汉化版
VANILLA = r"F:\sr2-cn\pristine\patch.vpp_pc"                                # 官方原版


def load_cl(vpp_path):
    v = Vpp(vpp_path)
    ce = v.find("charlist_CH", "txt")
    raw = v.read(ce)
    m = re.search(rb"count\s*=\s*(\d+)", raw)
    body = raw[m.end():] if m else raw
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


# ---------------------------------------------------------------- 读实测表
def read_pairs(path):
    import json
    cfg = json.load(open(path, encoding="utf-8"))
    return [(a, b) for a, b in cfg["pairs"]]


def main():
    cl_cn = load_cl(CN)
    cl_va = load_cl(VANILLA)
    print("简体版 charlist: %d 项" % len(cl_cn))
    print("原版   charlist: %d 项" % len(cl_va))
    print()

    # 按码点排序后的位置
    sorted_cn = sorted(range(len(cl_cn)), key=lambda i: cl_cn[i])
    rank_cn = {cl_cn[i]: r for r, i in enumerate(sorted_cn)}
    sorted_va = sorted(range(len(cl_va)), key=lambda i: cl_va[i])
    rank_va = {cl_va[i]: r for r, i in enumerate(sorted_va)}

    print("=" * 78)
    print("检验 1: 原版实测表 —— E(c) 是否 = 码点排名？")
    print("=" * 78)
    pairs_va = read_pairs(r"F:\sr2-cn\pairs_vanilla.json")
    print("  %-5s %-6s %-8s %-8s %-10s %-10s %s" %
          ("字", "码点", "clist索引", "排名", "E实测(格)", "排名-OFF", "匹配"))
    hit_rank = 0
    for c, d in pairs_va:
        ic = cl_va.index(ord(c)) if ord(c) in cl_va else -1
        idd = cl_va.index(ord(d)) if ord(d) in cl_va else -1
        if ic < 0 or idd < 0:
            print("  %-5s 不在表里" % c)
            continue
        E_measured = idd - OFFSET           # 引擎实际取的格
        rank = rank_va[ord(c)]
        ok = (rank - OFFSET) == E_measured
        if ok:
            hit_rank += 1
        print("  %-5s %-6d %-8d %-8d %-10d %-10d %s" %
              (c, ord(c), ic, rank, E_measured, rank - OFFSET, "✓" if ok else "✗"))
    print("  码点排名命中 %d/%d" % (hit_rank, len(pairs_va)))
    print()

    print("=" * 78)
    print("检验 2: 简体版实测表 —— 同上")
    print("=" * 78)
    pairs_cn = read_pairs(r"F:\sr2-cn\pairs_cn.json")
    print("  %-5s %-6s %-8s %-8s %-10s %-10s %s" %
          ("字", "码点", "clist索引", "排名", "E实测(格)", "排名-OFF", "匹配"))
    hit_rank2 = 0
    for c, d in pairs_cn:
        ic = cl_cn.index(ord(c)) if ord(c) in cl_cn else -1
        idd = cl_cn.index(ord(d)) if ord(d) in cl_cn else -1
        if ic < 0 or idd < 0:
            print("  %-5s 不在表里 (c=%s d=%s)" % (c, ic, idd))
            continue
        E_measured = idd - OFFSET
        rank = rank_cn[ord(c)]
        ok = (rank - OFFSET) == E_measured
        if ok:
            hit_rank2 += 1
        print("  %-5s %-6d %-8d %-8d %-10d %-10d %s" %
              (c, ord(c), ic, rank, E_measured, rank - OFFSET, "✓" if ok else "✗"))
    print("  码点排名命中 %d/%d" % (hit_rank2, len(pairs_cn)))
    print()

    # 检验 3：E(c) 是否 = clist索引 - OFFSET（恒等偏移）
    print("=" * 78)
    print("检验 3: E(c) 是否 = charlist索引 - OFFSET ?")
    print("=" * 78)
    for label, pairs, cl in (("原版", pairs_va, cl_va), ("简体", pairs_cn, cl_cn)):
        hit = 0
        tot = 0
        for c, d in pairs:
            ic = cl.index(ord(c)) if ord(c) in cl else -1
            idd = cl.index(ord(d)) if ord(d) in cl else -1
            if ic < 0 or idd < 0:
                continue
            tot += 1
            if (ic - OFFSET) == (idd - OFFSET):
                hit += 1
        print("  %s: E(c)==clist索引-OFFSET ? 命中 %d/%d" % (label, hit, tot))
    print()

    # 检验 4：E(c) 在图集里的实际内容
    print("=" * 78)
    print("检验 4: 反查 —— 「显示字 d」的 chartlist 索引 与「原字 c」的关系")
    print("=" * 78)
    for label, pairs, cl in (("原版", pairs_va, cl_va), ("简体", pairs_cn, cl_cn)):
        print("  --- %s ---" % label)
        for c, d in pairs[:10]:
            ic = cl.index(ord(c)) if ord(c) in cl else -1
            idd = cl.index(ord(d)) if ord(d) in cl else -1
            print("    c=%-3s(idx %-5d)  d=%-3s(idx %-5d)  d_idx-c_idx=%+d" %
                  (c, ic, d, idd, idd - ic))
        print()


if __name__ == "__main__":
    main()
