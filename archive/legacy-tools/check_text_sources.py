# -*- coding: utf-8 -*-
"""最终验证：游戏到底加载哪个 static_XX.le_strings？

线索
    patch.vpp_pc 里静态条目名：static_CH / static_CZ / static_DE / ...
    语言代码表（exe）：ru pl dk nl fr de it es en | RU SK CZ DK SE NL JP US
    forcelang 命令：en de fr es it nl se dk pl cz ru ch jp

问题
    "ch" 对应哪个代码？表里没有 CH？
    但 patch.vpp_pc 里确实有 static_CH（大写 CH）

推理
    forcelang_ch -> 游戏内部代码可能是 "CH"
    static_%s.le_strings -> "static_CH.le_strings"  ✓ 存在

    那么为什么改了没用？

本脚本
    1. 列出 patch.vpp_pc 里【所有】static_* 条目名
    2. 列出 common/textures/pegs 里的条目名（看是否有别的文本表）
    3. 检查 charlist_CH 是否被两处同时提供（patch 与 common）
"""
import os, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

for fn in ("patch.vpp_pc", "common.vpp_pc", "city_load.vpp_pc"):
    p = os.path.join(G, fn)
    print("=== %s ===" % fn)
    with LightVpp(p) as v:
        names = []
        for e in v.entries():
            nm = v.name(e)
            ex = v.ext(e)
            if nm.startswith(("static", "charlist", "platform", "voice_script", "hud", "subtitles")):
                names.append((nm, ex, e["size"]))
        for nm, ex, sz in sorted(names):
            print("  %-28s %-12s %8d" % (nm, ex or "-", sz))
        print("  （共 %d 条）" % len(names))
    print()

# 检查 patch.vpp_pc 里是否有 subtitles 相关
print("=== patch.vpp_pc 里含 'sub' / 'hud' / 'lua' 的条目 ===")
with LightVpp(os.path.join(G, "patch.vpp_pc")) as v:
    for e in v.entries():
        nm = v.name(e)
        low = nm.lower()
        if "sub" in low or "hud" in low or low.endswith(".lua") or "msg" in low:
            print("  %-40s %-10s %8d" % (nm, v.ext(e) or "-", e["size"]))
