# -*- coding: utf-8 -*-
"""决定性检验：M 是否按 GBK / Big5 / 其它编码顺序排序？

假设
    引擎的字符表 M 按【编码字节序】排列，而不是 Unicode 码点序。
    简体版 -> GBK/GB2312
    繁中版 -> Big5

如果成立：
    E(c) - OFFSET = rank_encoding(c)
    其中 rank_encoding(c) = c 在 charlist 按该编码字节升序排序后的位置
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


def key_for(cp, enc):
    """返回该字符在指定编码下的排序键；编码不出来的排到最后"""
    try:
        b = chr(cp).encode(enc)
        return (0, b)
    except Exception:
        return (1, b"")


def test(label, vpp, pairfile):
    cl = load_cl(vpp)
    IDX = {cp: i for i, cp in enumerate(cl)}
    cfg = json.load(open(pairfile, encoding="utf-8"))
    pairs = cfg["pairs"]

    print("=" * 82)
    print("%s  (charlist %d 项, 实测 %d 对)" % (label, len(cl), len(pairs)))
    print("=" * 82)

    for enc in ("gbk", "gb18030", "big5", "big5hkscs", "cp950", "utf-8"):
        order = sorted(range(len(cl)), key=lambda i: key_for(cl[i], enc))
        rank = {}
        for r, i in enumerate(order):
            rank[cl[i]] = r
        hit = 0
        tot = 0
        misses = []
        for c, d in pairs:
            oc, od = ord(c), ord(d)
            if oc not in rank or od not in IDX:
                continue
            tot += 1
            E_measured = IDX[od] - OFFSET
            pred = rank[oc] - OFFSET
            if pred == E_measured:
                hit += 1
            else:
                misses.append((c, d, E_measured, pred))
        print("  编码 %-10s 命中 %2d/%-2d  %s" %
              (enc, hit, tot, "★ 全部命中!" if hit == tot and tot > 0 else ""))

    # 详细看 GBK
    print()
    print("  --- 详细：GBK 排序 ---")
    order = sorted(range(len(cl)), key=lambda i: key_for(cl[i], "gbk"))
    rank = {cl[i]: r for r, i in enumerate(order)}
    print("  %-4s %-8s %-8s %-9s %-9s %s" % ("字", "码点", "clist", "E实测", "GBK排名-OFF", "匹配"))
    for c, d in pairs[:15]:
        oc, od = ord(c), ord(d)
        if oc not in rank or od not in IDX:
            print("  %-4s 不在表" % c)
            continue
        E = IDX[od] - OFFSET
        pred = rank[oc] - OFFSET
        print("  %-4s %-8d %-8d %-9d %-9d %s" %
              (c, oc, IDX[oc], E, pred, "✓" if pred == E else "✗"))
    print()


if __name__ == "__main__":
    test("官方原版（繁中）", VANILLA, r"F:\sr2-cn\pairs_vanilla.json")
    test("简体汉化版", CN, r"F:\sr2-cn\pairs_cn.json")
