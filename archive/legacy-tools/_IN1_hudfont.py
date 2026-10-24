# -*- coding: utf-8 -*-
# 只读: hud.lua 里 font 属性 与 region 的对应
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))

for nm in ["hud", "hud_msg"]:
    e = v.find(nm, "lua")
    if not e:
        print("!! %s not found" % nm); continue
    d = v.read(e).decode("latin1")
    print("=" * 70)
    print("[%s.lua] %d B" % (nm, len(d)))
    lines = d.split("\n")
    for i, ln in enumerate(lines):
        if "font" in ln.lower():
            print("  %4d| %s" % (i + 1, ln.rstrip()[:130]))
