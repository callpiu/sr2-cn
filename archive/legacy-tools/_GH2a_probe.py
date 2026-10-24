# -*- coding: utf-8 -*-
"""GH2a: 只读探查 —— 哪些 VPP 含 hud_msg 条目，目标串出现几次。"""
import sys, os, glob
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OLD = b'vint_set_property(o, "font", "thin_overlay")'
NEW = b'vint_set_property(o, "font", "fnt_chinese")'
print("OLD len=%d NEW len=%d" % (len(OLD), len(NEW)))

lp = os.path.join(G, "Mods", "hud_msg.lua")
if os.path.exists(lp):
    b = open(lp, "rb").read()
    print("\n[松散] %s  %d B  旧串 %d 处  新串 %d 处" % (lp, len(b), b.count(OLD), b.count(NEW)))
else:
    print("\n[松散] 不存在:", lp)

print("\n=== VPP ===")
for vp in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(vp)
    except Exception as ex:
        print("[%s] 打开失败 %s" % (os.path.basename(vp), ex)); continue
    hit = 0
    for e in v.entries():
        if (e["name"] or "") == "hud_msg":
            raw = v.read(e)
            hit += 1
            print("[%s] hud_msg.%s  %d B  旧串 %d  新串 %d" % (
                os.path.basename(vp), e["ext"], len(raw), raw.count(OLD), raw.count(NEW)))
    if hit == 0:
        print("[%s] 无 hud_msg" % os.path.basename(vp))
