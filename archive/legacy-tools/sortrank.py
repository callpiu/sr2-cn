# -*- coding: utf-8 -*-
"""验证：运行时 idx = 码点在排序后字表中的名次？"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/stub")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in vp.read(vp.find("charlist_CH")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
N = len(cps)
print("N =", N, " 已排序？", all(cps[i] <= cps[i+1] for i in range(N-1)))

srt = sorted(cps)
rank = {}
for i, cp in enumerate(srt):
    rank.setdefault(cp, i)   # 重复码点取第一个

BAD = {"会": (348, "伙"), "三": (239, "丈"), "律": (1057, "延"),
       "徒": (1058, "建"), "得": (1059, "开"), "必": (1066, "弗"),
       "心": (1065, "引"), "联": (2100, "伙?")}
GOOD = {"人": (344, "人"), "帮": (992, "帮"), "计": (2312, "计"),
        "赚": (2405, "赚"), "社": (1908, "社"), "主": (751, "主"),
        "城": (237, "城"), "老": (268, "老"), "郊": (30, "郊")}

print("\n%-4s %-6s %-6s %-6s %-8s %s" % ("字", "本idx", "排序名次", "差", "该名次的字", "状态"))
for tag, d in (("坏", BAD), ("好", GOOD)):
    for ch, (i, disp) in d.items():
        cp = cps[i]
        r = rank.get(cp, -1)
        shown = chr(srt[r]) if 0 <= r < N else "?"
        ok = "✓命中" if shown == disp else ""
        print("%-4s %-6d %-8d %-6d %-8s %s %s"
              % (ch + "(%s)" % tag, i, r, r - i, shown, disp, ok))
