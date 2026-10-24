# -*- coding: utf-8 -*-
"""读 patch.vpp_pc 里的 hud_msg.lua（字幕模块）。"""
import os, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_fontfix_out"
os.makedirs(OUT, exist_ok=True)

with LightVpp(os.path.join(G, "patch.vpp_pc")) as v:
    for nm in ("hud_msg", "hud"):
        e = None
        for x in v.entries():
            if v.name(x) == nm and v.ext(x) == "lua":
                e = x
                break
        if e is None:
            print("%s.lua 未找到" % nm)
            continue
        d = v.read(e)
        p = os.path.join(OUT, nm + ".lua")
        open(p, "wb").write(d)
        print("=== %s.lua (%d 字节) -> %s ===" % (nm, len(d), p))
        try:
            t = d.decode("utf-8")
        except UnicodeDecodeError:
            t = d.decode("latin1")
        lines = t.split("\n")
        # 打印含 font / subtitle / text 的行
        for i, ln in enumerate(lines, 1):
            low = ln.lower()
            if any(k in low for k in ("font", "subtitle", "vint_set_property", "text_tag",
                                      "region", "wrap", "scale")):
                print("  %4d: %s" % (i, ln.rstrip()[:150]))
        print()
