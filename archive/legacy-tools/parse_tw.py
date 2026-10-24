import os, sys, hashlib
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
p = r"F:\sr2-cn\_tw_patch\patch.vpp_pc"
v = Vpp(p)
print("=== IdolNinja 官方多语言补丁 patch.vpp_pc ===")
print("  %d 条目, %d 字节, md5 %s" % (v.num, os.path.getsize(p), hashlib.md5(open(p,'rb').read()).hexdigest()))
print()
print("=== 所有 le_strings 条目 ===")
for e in sorted(v.entries(), key=lambda x: (x["name"], x["ext"] or "")):
    if e["ext"] == "le_strings":
        print("  %-26s %9d" % (e["name"], e["size"]))
print()
print("=== 字符表 / 字体条目 ===")
for e in sorted(v.entries(), key=lambda x: (x["name"], x["ext"] or "")):
    if e["name"].startswith("charlist") or e["name"].startswith("fnt_"):
        print("  %-26s %-10s %9d" % (e["name"], e["ext"] or "-", e["size"]))
