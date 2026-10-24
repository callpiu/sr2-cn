# -*- coding: utf-8 -*-
"""GG1: 用新截图的乱码字形反推「槽位 -> 实际渲染字符」的索引变换。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(os.path.join(G, "patch.vpp_pc"))
T = [int(s) for s in pv.read(pv.find("charlist_CH", "txt")).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]
pos = {}
for i, c in enumerate(T):
    pos.setdefault(c, i)
print("charlist=%d  cp范围 %d..%d" % (len(T), min(T), max(T)))

def idx(ch):
    return pos.get(ord(ch), None)

# 期望文本（来自 static_CH）与截图观测文本
PAIRS = [
    ("SUB1 你的弟兄们需要你的保护", "你的弟兄们需要你的保护", "任璨巧位雄衡任璨伪该"),
    ("SUB3 你的弟兄们要出去谈几笔生意，保护他们免遭袭击",
     "你的弟兄们要出去谈几笔生意，保护他们免遭袭击",
     "任璨巧位校衡勾远藐乱撕伪该亡位通像匪冰挺括"),
]

for tag, exp, obs in PAIRS:
    print("=" * 78)
    print("[%s]" % tag)
    print("  期望:", exp, "  (%d 字)" % len(exp))
    print("  观测:", obs, "  (%d 字)" % len(obs))
    n = min(len(exp), len(obs))
    print("  %-4s %-4s %-8s %-8s %-8s" % ("#", "字", "期望槽位", "实渲染槽位", "差"))
    rows = []
    for k in range(n):
        a, b = exp[k], obs[k]
        ia, ib = idx(a), idx(b)
        if ia is None or ib is None:
            print("  %-4d %s->%s  (查表失败 %s %s)" % (k, a, b, ia, ib)); continue
        sa, sb = ia + 32, ib + 32
        rows.append((sa, sb))
        print("  %-4d %-4s %-8d %-8d %+d" % (k, "%s->%s" % (a, b), sa, sb, sb - sa))
    if len(rows) >= 3:
        ds = [b - a for a, b in rows]
        print("  差值序列:", ds)
        print("  是否恒定:", len(set(ds)) == 1, " 中位:", sorted(ds)[len(ds)//2])
        # 是否单调递增（保序变换）
        inc = all(rows[i][1] < rows[i+1][1] for i in range(len(rows)-1))
        print("  实渲染槽位单调递增:", inc)
