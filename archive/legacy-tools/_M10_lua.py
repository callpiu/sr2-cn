# -*- coding: utf-8 -*-
# 列 patch.vpp_pc 里的 lua 条目，找直升机突击 / 活动相关的 lua
import sys, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
cn = Vpp(os.path.join(G, "patch.vpp_pc"))
print("=== patch.vpp_pc 中的 lua 条目 ===")
for e in cn.entries():
    if (e["ext"] or "").lower() in ("lua", "lt2", "lub"):
        print("  %-34s %-8s %9d" % (e["name"], e["ext"], e["size"]))

# 关键：hud_msg.lua 里 font 设置与字符串引用
for target in ("hud_msg", "hud", "dialog_box", "tutorial", "activity"):
    e = cn.find(target, "lua")
    if not e:
        continue
    d = cn.read(e)
    print("\n=== %s.lua (%d B) 前 1200 字节可打印部分 ===" % (target, len(d)))
    s = "".join(chr(b) if 32 <= b < 127 else "." for b in d[:1200])
    print(s)
