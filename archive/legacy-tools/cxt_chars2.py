import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"; G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = set(CPS)
s = open(G + r"\Mods\JUICED - Strings\juiced_CH.cxt", encoding="utf-8").read()
print("=== .cxt 里所有 CJK 字符是否在字符表里 ===")
cjk = sorted({c for c in s if 0x100 < ord(c) < 0x9FFF})
miss = [c for c in cjk if ord(c) not in S]
print("  .cxt 用到 CJK %d 个，缺 %d 个: %s" % (len(cjk), len(miss), "".join(miss) if miss else "无"))
print()
# 逐行看
print("=== 逐条目检查 ===")
lines = s.split("\r\n")
cur = None
for ln in lines:
    if ln.startswith("[") and ln.endswith("]"):
        cur = ln
    elif ln.strip() and cur:
        m = [c for c in ln if 0x100 < ord(c) < 0x9FFF and ord(c) not in S]
        tag = "缺 "+"".join(m) if m else "OK"
        print("  %-18s %-24s %s" % (cur, ln, tag))
