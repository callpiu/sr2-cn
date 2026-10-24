# -*- coding: utf-8 -*-
"""GH2c: 对比 patch.vpp_pc 内 hud_msg.lua 与松散 Mods/hud_msg.lua，
列出所有含 font/thin/fnt 的行。"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def show(buf, label):
    txt = buf.decode("utf-8", "replace")
    lines = txt.splitlines()
    print("\n===== %s  %d B  %d 行 =====" % (label, len(buf), len(lines)))
    for i, ln in enumerate(lines, 1):
        if re.search(r"font|thin|fnt_|overlay", ln, re.I):
            print("  %5d | %s" % (i, ln.strip()[:200]))

# 松散
lp = os.path.join(G, "Mods", "hud_msg.lua")
show(open(lp, "rb").read(), "松散 Mods/hud_msg.lua")

# VPP 内
v = Vpp(os.path.join(G, "patch.vpp_pc"))
for e in v.entries():
    if (e["name"] or "") == "hud_msg" and e["ext"] == "lua":
        show(v.read(e), "patch.vpp_pc/hud_msg.lua")
