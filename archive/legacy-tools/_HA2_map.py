# -*- coding: utf-8 -*-
"""对每个候选字体字形表 C：把 le_strings 每条记录的槽位映射成 C.decode(units)，
   查找能还原出「任璨偶巧位」的记录。命中即可反推正确文本。"""
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
from sr2strings import StringsFile, CharList

G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PR = r"F:/sr2-cn/pristine/patch.vpp_pc"

def cl_from(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    if nums and nums[0] == len(nums) - 1: nums = nums[1:]
    return CharList(nums)

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
cl2795 = cl_from(cn.read(cn.find("charlist_CH", "txt")))

cands = {"CH2795": cl2795}
for nm in ["charlist_JP", "charlist_CZ", "charlist_PL", "charlist_RU", "charlist_SK"]:
    e = cn.find(nm, "txt")
    if e: cands[nm] = cl_from(cn.read(e))
pv = Vpp(PR)
e = pv.find("charlist_CH", "txt")
cands["CH2838_official"] = cl_from(pv.read(e))
for k, c in cands.items():
    print(f"{k}: {len(c.body)}")

# 收集全部记录
recs = []
for e in cn.entries():
    if e['ext'].lower() != 'le_strings': continue
    nm = e['name'] + '.' + e['ext']
    sf = StringsFile(data=cn.read(e))
    for i, off, t, L in sf.all_records(cl2795):
        r = sf.read_record(off)
        recs.append((nm, i, r[2], t))
print("records =", len(recs))

NEED = "任璨"
for k, c in cands.items():
    hits = 0
    for nm, i, units, t in recs:
        d = c.decode(units)
        if d and NEED in d:
            print(f"  [{k}] {nm} idx={i}\n     显示: {d[:70]}\n     正确: {t[:70]}")
            hits += 1
            if hits >= 5: break
    print(f"{k}: hits={hits}")
