# -*- coding: utf-8 -*-
"""验证核心假设：
   现役 slot 序列是按【第三方 2795 项字表】编码的，
   但游戏运行时可能加载的是【原厂 charlist_CH】。
   若 idx 在两表之间指向不同字 -> 就能解释「显示成别的字」。
"""
import sys, io, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

sys.stdout.reconfigure(encoding="utf-8")


def load(p, tag):
    v = Vpp(p)
    raw = v.read(v.find("charlist_CH", "txt"))
    txt = raw.decode("utf-8")
    cps = [int(l) for l in txt.split("\n") if l.strip().isdigit()]
    print("%-6s %-38s %8d bytes  %5d 项  末项=%r" % (
        tag, os.path.basename(p), len(raw), len(cps),
        txt.strip().split("\n")[-1][:40]))
    return cps


print("### 1. 两张 charlist_CH 对比")
orig = load(r"F:\sr2-cn\pristine\patch.vpp_pc", "原厂")
cur = load(r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc", "现役")

print()
print("### 2. 关键 slot 在两表中的字（slot = idx + 0x20）")
targets = [
    ("辩", 2506), ("护", 1222), ("律", 1089), ("延", 1057), ("师", 1013),
    ("三", 271), ("丈", 270), ("王", 1796),
]
print("  词  slot  原厂idx  原厂字  |  现役idx  现役字  | 一致?")
for ch, slot in targets:
    idx = slot - 0x20
    a = chr(orig[idx]) if 0 <= idx < len(orig) else "<越界>"
    b = chr(cur[idx]) if 0 <= idx < len(cur) else "<越界>"
    print("  %s  %5d  %6d  %5s  |  %6d  %5s  | %s" % (
        ch, slot, idx, a, idx, b, "同" if a == b else "★不同★"))

print()
print("### 3. 整体一致度")
n = min(len(orig), len(cur))
same = sum(1 for i in range(n) if orig[i] == cur[i])
print("  共同长度 %d 项，其中码点相同 %d 项 (%.2f%%)" % (n, same, 100.0 * same / n))
diff = [i for i in range(n) if orig[i] != cur[i]]
print("  不同项数 %d" % len(diff))
if 0 < len(diff) <= 60:
    print("  前若干不同位置:")
    for i in diff[:40]:
        a = chr(orig[i]) if orig[i] > 32 else "?"
        b = chr(cur[i]) if cur[i] > 32 else "?"
        print("    idx %5d : 原厂 U+%04X %s  ->  现役 U+%04X %s" % (
            i, orig[i], a, cur[i], b))