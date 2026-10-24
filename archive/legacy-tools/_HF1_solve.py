# -*- coding: utf-8 -*-
"""用已知对照（正确字 -> 显示字）反推引擎的字形查找规则。
正确: 你的弟兄们需要你的保护
显示: 任璨偶巧位雄衡任璨伪该   (日志已实锤)"""
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PR = r"F:/sr2-cn/pristine/patch.vpp_pc"

def load_cl(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    if nums and nums[0] == len(nums) - 1: nums = nums[1:]
    rev = {}
    for i, cp in enumerate(nums): rev.setdefault(cp, i)
    return nums, rev

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
pv = Vpp(PR)
CL = {"CH2795": load_cl(cn.read(cn.find("charlist_CH", "txt")))}
for nm in ["charlist_JP","charlist_CZ","charlist_PL","charlist_RU","charlist_SK"]:
    e = cn.find(nm, "txt")
    if e: CL[nm] = load_cl(cn.read(e))
CL["CH_official"] = load_cl(pv.read(pv.find("charlist_CH", "txt")))
print({k: len(v[0]) for k, v in CL.items()})

# 日志给出的 9 组对照 (正确字, 显示字)
PAIRS = [("你","任"),("的","璨"),("弟","偶"),("兄","巧"),("们","位"),
         ("需","雄"),("要","衡"),("保","伪"),("护","该")]

body2795, rev2795 = CL["CH2795"]
print("\n正确字 -> 槽位(=idx+32) -> 显示字")
for c, d in PAIRS:
    i = rev2795.get(ord(c))
    print(f"  {c}(U+{ord(c):04X}) idx={i} slot={None if i is None else i+32}  ->  {d}(U+{ord(d):04X})")

print("\n=== H1: 显示字 == C[slot-32] ？ ===")
for name, (b, r) in CL.items():
    ok = 0; det = []
    for c, d in PAIRS:
        i = rev2795.get(ord(c))
        if i is None or i >= len(b): det.append("?"); continue
        got = chr(b[i])
        det.append(got)
        if got == d: ok += 1
    print(f"  {name:12s} 命中 {ok}/9   {''.join(det)}")

print("\n=== H2: 显示索引 == 正确码点在 C 中的位置？ ===")
for name, (b, r) in CL.items():
    ok = 0; det = []
    for c, d in PAIRS:
        j = r.get(ord(c))
        if j is None: det.append("?"); continue
        got = chr(b[j]) if j < len(b) else "?"
        det.append(got)
        if got == d: ok += 1
    print(f"  {name:12s} 命中 {ok}/9   {''.join(det)}")

print("\n=== H3: 显示索引 = 正确索引的某种排序位置？(按 U/V 或宽度排序) ===")
# 直接看差值
for c, d in PAIRS:
    i = rev2795.get(ord(c)); j = rev2795.get(ord(d))
    print(f"  {c} idx={i} -> {d} idx={j}  diff={None if None in (i,j) else j-i}")
