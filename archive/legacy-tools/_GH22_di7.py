# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
A = Vpp(r"F:/sr2-cn/pristine/patch.vpp_pc")
B = Vpp(r"F:/sr2-cn/_zip92/黑道圣徒2简体汉化补丁/patch.vpp_pc")
da = {(e["name"] or "") + "." + (e["ext"] or ""): e for e in A.entries()}
db = {(e["name"] or "") + "." + (e["ext"] or ""): e for e in B.entries()}
print("原版 %d 条 / 汉化 %d 条" % (len(da), len(db)))
only_a = sorted(set(da) - set(db)); only_b = sorted(set(db) - set(da))
print("\n仅原版有 (%d):" % len(only_a))
for k in only_a[:20]: print("   -", k)
print("\n仅汉化有 (%d):" % len(only_b))
for k in only_b[:20]: print("   +", k)
print("\n同名但大小不同:")
n = 0
for k in sorted(set(da) & set(db)):
    if da[k]["size"] != db[k]["size"]:
        print("   %-30s 原版 %8d -> 汉化 %8d" % (k, da[k]["size"], db[k]["size"])); n += 1
print("   共 %d 条" % n)
