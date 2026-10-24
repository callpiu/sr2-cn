# -*- coding: utf-8 -*-
"""GH6: 搜所有 VPP 里含 'thin'/'overlay' 的条目名，以及 pegs 里的字体资源名列表。"""
import sys, os, glob, re
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

print("=== 1) 所有 VPP 中含 thin/overlay 的条目名 ===")
for vp in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(vp)
    except Exception as ex:
        continue
    hits = []
    for e in v.entries():
        nm = ((e["name"] or "") + "." + (e["ext"] or ""))
        if re.search(r"thin|overlay|fnt_|font", nm, re.I):
            hits.append(nm)
    if hits:
        print("\n[%s] %d 个" % (os.path.basename(vp), len(hits)))
        for h in sorted(set(hits)):
            print("   ", h)

print("\n=== 2) pegs.vpp_pc 里所有条目名 ===")
v = Vpp(os.path.join(G, "pegs.vpp_pc"))
names = sorted(set(((e["name"] or "") + "." + (e["ext"] or "")) for e in v.entries()))
print("总条目 %d" % len(names))
for n in names:
    print("   ", n)
