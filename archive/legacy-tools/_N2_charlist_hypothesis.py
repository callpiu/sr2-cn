# -*- coding: utf-8 -*-
"""决定性检验：简体补丁是否重排了 charlist_CH，而引擎的 M 仍按原版顺序？

假说
    引擎的字符表 M 位置 = 字符在【原版（繁中）charlist】里的索引 - OFFSET
    简体补丁重排了 charlist_CH（贴图集重新排了字形），导致：
        显示字 d 满足  clist_cn.index(d) == clist_va.index(c)
    即：用原版的索引去查简体版的 charlist

检验
    对每对 (原字 c, 显示字 d)：
        预测 = clist_va.index(c)
        实际 = clist_cn.index(d)
        两者应相等
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

print("原版 charlist: %d 项" % len(cl_va))
print("简体 charlist: %d 项" % len(cl_cn))
print()

print("=" * 84)
print("检验：clist_cn.index(显示字) == clist_va.index(原字) ?")
print("=" * 84)
cfg = json.load(open(r"F:\sr2-cn\pairs_cn.json", encoding="utf-8"))
print("  %-4s %-8s %-8s %-10s %-10s %s" %
      ("原字", "va_idx", "显示字", "cn_idx(实测)", "va_idx(预测)", "匹配"))
hit = 0
tot = 0
for c, d in cfg["pairs"]:
    oc, od = ord(c), ord(d)
    iva = IVA.get(oc, -1)
    icn = ICN.get(od, -1)
    ok = (iva == icn)
    if iva >= 0 and icn >= 0:
        tot += 1
        if ok:
            hit += 1
    print("  %-4s %-8s %-8s %-10s %-10s %s" %
          (c, iva if iva >= 0 else "-", d, icn if icn >= 0 else "-",
           iva if iva >= 0 else "-", "✓" if ok else "✗"))
print()
print("  ★ 命中 %d/%d" % (hit, tot))
print()

# 换个角度：显示字 d 在 cn 的索引 是否等于 原字 c 在 va 的索引？
print("=" * 84)
print("换个等价表述：检查「简体 charlist 是否 = 原版 charlist 的重排」")
print("=" * 84)
# 两版共有的字符，看它们的相对顺序是否一致
common = [cp for cp in cl_cn if cp in IVA]
print("  简体表 %d 项，其中 %d 项在原版表里也有" % (len(cl_cn), len(common)))
# 检查共同字符在两版中的顺序是否相同
seq_cn = [cp for cp in cl_cn if cp in IVA]
seq_va = [cp for cp in cl_va if cp in ICN]
print("  共同字符序列是否完全相同? %s" % ("是（顺序一致）" if seq_cn == seq_va else "否（顺序不同）"))
if seq_cn != seq_va:
    # 找第一处不同
    for i, (a, b) in enumerate(zip(seq_cn, seq_va)):
        if a != b:
            print("  第一处不同在共同序列位置 %d: 简体=%s(U+%04X)  原版=%s(U+%04X)" %
                  (i, chr(a), a, chr(b), b))
            print("  附近:")
            for j in range(max(0, i - 3), min(len(seq_cn), i + 4)):
                print("    [%d] 简体 %s (U+%04X)   原版 %s (U+%04X)" %
                      (j, chr(seq_cn[j]), seq_cn[j], chr(seq_va[j]), seq_va[j]))
            break
print()

# 只在简体表里 / 只在原版表里的字
only_cn = [cp for cp in cl_cn if cp not in IVA]
only_va = [cp for cp in cl_va if cp not in ICN]
print("  只在简体表里: %d 个  %s" % (len(only_cn), "".join(chr(x) for x in only_cn[:60])))
print("  只在原版表里: %d 个  %s" % (len(only_va), "".join(chr(x) for x in only_va[:60])))
