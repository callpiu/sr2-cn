# -*- coding: utf-8 -*-
# 看 tutorial_subtitles.lua 全文（教程字幕 = thin_overlay 路径）
import sys, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
cn = Vpp(os.path.join(G, "patch.vpp_pc"))
for target in ("tutorial_subtitles", "tutorial"):
    e = cn.find(target, "lua")
    if not e:
        continue
    d = cn.read(e)
    print("=" * 70)
    print("=== %s.lua (%d B) ===" % (target, len(d)))
    print("=" * 70)
    for i, line in enumerate(d.decode("utf-8", "replace").split("\n"), 1):
        print("%4d| %s" % (i, line[:115]))
