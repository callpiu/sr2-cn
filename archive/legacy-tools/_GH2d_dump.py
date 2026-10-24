# -*- coding: utf-8 -*-
"""GH2d: 导出 patch.vpp_pc 内 hud_msg.lua 全文到 F:\\sr2-cn\\_hud_msg_patch.lua"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_hud_msg_patch.lua"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
for e in v.entries():
    if (e["name"] or "") == "hud_msg" and e["ext"] == "lua":
        raw = v.read(e)
        open(OUT, "wb").write(raw)
        print("导出 %d B -> %s" % (len(raw), OUT))
        # 打印 90-130 行
        lines = raw.decode("utf-8", "replace").splitlines()
        for i in range(85, min(135, len(lines))):
            print("%5d | %s" % (i + 1, lines[i]))
