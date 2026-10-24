# -*- coding: utf-8 -*-
"""在汉化 patch.vpp_pc 的所有 le_strings 里，用 2795 项 charlist 解码，
   查找解出「任璨偶巧位」的记录。"""
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
from sr2strings import StringsFile, CharList

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
ents = v.entries()

def cl_from(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    if nums and nums[0] == len(nums) - 1:
        nums = nums[1:]
    return CharList(nums)

cl2795 = cl_from(v.read(v.find("charlist_CH", "txt")))
print("CL2795 =", len(cl2795.body))

TARGET = "任璨偶巧位"
hits = 0
for e in ents:
    nm = e['name'] + ('.' + e['ext'] if e['ext'] else '')
    if e['ext'].lower() != 'le_strings':
        continue
    sf = StringsFile(data=v.read(e))
    for i, off, t, L in sf.all_records(cl2795):
        if "任璨" in t or "偶巧" in t:
            print(f"  [{nm}] idx={i} units={L}  {t[:80]}")
            hits += 1
print("hits =", hits)
