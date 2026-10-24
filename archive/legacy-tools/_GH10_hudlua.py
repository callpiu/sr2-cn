# -*- coding: utf-8 -*-
"""GH10: dump patch.vpp_pc 内所有 hud*.lua 里含 thin/overlay/fnt_ 的行（带行号）。"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))

for e in sorted(v.entries(), key=lambda x: (x["name"] or "")):
    nm = (e["name"] or "")
    if not re.search(r"hud", nm, re.I) or e["ext"] != "lua":
        continue
    raw = v.read(e)
    txt = raw.decode("utf-8", "replace")
    lines = txt.splitlines()
    hits = [(i, ln) for i, ln in enumerate(lines, 1)
            if re.search(r"thin|overlay|fnt_|font", ln, re.I)]
    print("\n===== %s.%s  %d B / %d 行  命中 %d =====" % (nm, e["ext"], len(raw), len(lines), len(hits)))
    for i, ln in hits:
        print("  %5d | %s" % (i, ln.strip()[:180]))
