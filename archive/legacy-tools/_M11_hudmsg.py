# -*- coding: utf-8 -*-
# 看 hud_msg.lua 全文：它显示什么、从哪取字符串、font 怎么设
import sys, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
cn = Vpp(os.path.join(G, "patch.vpp_pc"))

for target in ("hud_msg", "activity_level"):
    e = cn.find(target, "lua")
    if not e:
        print("找不到", target); continue
    d = cn.read(e)
    print("\n" + "=" * 70)
    print("=== %s.lua  (%d B) ===" % (target, len(d)))
    print("=" * 70)
    # lua 是明文（非编译），直接按行输出
    txt = d.decode("utf-8", "replace")
    for i, line in enumerate(txt.split("\n"), 1):
        print("%4d| %s" % (i, line[:110]))
