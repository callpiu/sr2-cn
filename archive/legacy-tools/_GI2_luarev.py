# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
NEW = b'"fnt_chinese"'
for fn in ("hud_msg.lua", "hud.lua"):
    lp = os.path.join(G, "Mods", fn)
    lines = open(lp, "rb").read().split(b"\n")
    hit = [(i+1, l) for i, l in enumerate(lines) if NEW in l]
    print("\n%s: %d 处含 fnt_chinese" % (fn, len(hit)))
    for i, l in hit:
        print("   %d | %s" % (i, l.strip()[:120]))
