# -*- coding: utf-8 -*-
"""GH5: dump 当前游戏 common.vpp_pc 里的 sr2.vint_proj 全文。"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "common.vpp_pc"))
for e in v.entries():
    if (e["name"] or "") == "sr2" and e["ext"] == "vint_proj":
        raw = v.read(e)
        print("sr2.vint_proj %d B" % len(raw))
        open(r"F:\sr2-cn\_sr2.vint_proj.cur", "wb").write(raw)
        # 全部可打印串
        for m in re.finditer(rb"[\x20-\x7e]{3,}", raw):
            print("  @%06X  %s" % (m.start(), m.group().decode("ascii")))
