# -*- coding: utf-8 -*-
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, parse_charlist
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PR = r"F:/sr2-cn/pristine/patch.vpp_pc"
cn = Vpp(os.path.join(G, "patch.vpp_pc")); pv = Vpp(PR)

a = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))
o = parse_charlist(pv.read(pv.find("charlist_CH", "txt")))
print("汉化 charlist =", len(a), " 官方 charlist =", len(o))

PAIRS = [(371,"任"),(1836,"璨"),(1035,"偶"),(422,"巧"),(332,"位"),
         (2667,"雄"),(2296,"衡"),(391,"伪"),(1190,"该")]
print("\n=== 显示字 == 官方charlist[i] ? ===")
det = []
for i, want in PAIRS:
    got = chr(o[i]) if i < len(o) else "?"
    det.append(got)
    mark = "OK" if got == want else "  "
    print(f"  i={i:5d} 期望 {want}  官方表给出 {got}  {mark}")
print("  →", "".join(det))

# 也检查：官方表里这些字的位置
rev = {}
for k, cp in enumerate(o): rev.setdefault(cp, k)
print("\n=== 期望字在官方表中的位置 ===")
for i, want in PAIRS:
    print(f"  期望 {want}(U+{ord(want):04X}) 官方位置 = {rev.get(ord(want))}   汉化位置 = {i}")

print("\n=== 两表前 40 项差异 ===")
for k in range(min(40, len(a), len(o))):
    if a[k] != o[k]:
        print(f"  首个不同在 k={k}: 汉化 {a[k]} 官方 {o[k]}")
        break
else:
    print("  前 40 项相同")
# 找第一个不同
for k in range(min(len(a), len(o))):
    if a[k] != o[k]:
        print(f"  第一个不同 k={k}: 汉化 {a[k]}(U+{a[k]:04X}) 官方 {o[k]}(U+{o[k]:04X})")
        break
