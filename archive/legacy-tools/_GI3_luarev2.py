# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
NEW = b'"fnt_chinese"'
PLAN = {"hud_msg.lua": [(131, b'"thin_overlay"')],
        "hud.lua":     [(3223, b'"thin"'), (3227, b'"thin_overlay"')]}
for fn, plan in PLAN.items():
    lp = os.path.join(G, "Mods", fn)
    lines = open(lp, "rb").read().split(b"\n")
    for ln, val in plan:
        i = ln - 1
        if i < len(lines) and NEW in lines[i]:
            lines[i] = lines[i].replace(NEW, val)
            print("  %s 第%d行 -> %s" % (fn, ln, val.decode()))
    open(lp, "wb").write(b"\n".join(lines))
    # 校验
    b = open(lp, "rb").read()
    print("  %s: fnt_chinese %d 处 / thin_overlay %d 处" % (fn, b.count(NEW), b.count(b'"thin_overlay"')))
