import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"; G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = set(CPS)
print("第三方 charlist %d 项" % len(CPS))
print()
# 读 .cxt 的所有值
s = open(G + r"\Mods\JUICED - Strings\juiced_CH.cxt", encoding="utf-8").read()
vals = []
for m in re.finditer(r'\[([A-Za-z0-9_]+)\]\r\n(.*?)\r\n', s):
    vals.append((m.group(1), m.group(2)))
print("=== .cxt 各条目的中文用字是否都在字符表里 ===")
bad_any = 0
for k, val in vals:
    miss = sorted({c for c in val if ord(c) > 0x100 and ord(c) not in S})
    if miss:
        print("  [%-16s] %-22s 缺: %s" % (k, val, "".join(miss)))
        bad_any += 1
print()
print("有缺字的条目: %d / %d" % (bad_any, len(vals)))
