# -*- coding: utf-8 -*-
"""从面板+字幕的实例反推「错字规律」。

已知实例
  A) 面板: 正确「直升機突擊」  ->  屏幕「直升機攻擊」
        突 (idx ?) -> 攻 (idx ?)
  B) 字幕: 正确「兄弟們要出去…」->  屏幕「使發光彈借步…」

如果这其实是「字体图集里某一段格子被整体错位」，那么
   屏幕字 = charlist[ 期望索引 + Δ ]  且 Δ 在不同区段不同
本脚本
  1. 收集所有已知的「期望字 -> 屏幕字」对
  2. 计算 Δ = 屏幕索引 - 期望索引
  3. 检查 Δ 是否与「期望索引所在的区段」相关（分段常量）
"""
import os, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    for e in pv.entries():
        if pv.name(e) == "charlist_CH":
            cn = [int(l) for l in pv.read(e).decode("utf-8", "replace").split("\n") if l.strip().isdigit()]
            break
IDX = {chr(cp): i for i, cp in enumerate(cn)}
N = len(cn)
print("charlist_CH: %d 项" % N)
print()

# 收集所有已知映射对（来自截图与 static_CH 数据）
PAIRS = [
    # A) 面板：直升機突擊 -> 直升機攻擊
    ("突", "攻"),
    # B) 字幕：static_CH 0x10AF1E62 的真实槽位 vs 用户截图
    ("兄", "使"), ("弟", "發"), ("們", "光"), ("正", "彈"),
    ("要", "借"), ("去", "步"), ("進", "復"), ("行", "友"),
    ("交", "途"), ("易", "螢"), ("，", "交"), ("保", "星"),
    ("護", "點"), ("他", "俱"), ("避", "仙"), ("免", "遞"),
    ("受", "全"), ("到", "句"), ("攻", "剝"), ("擊", "放"),
]

print("=== 期望字 -> 屏幕字，Δ = 屏幕idx - 期望idx ===")
print("  %-6s %-8s %-6s %-8s %-8s" % ("期望", "期望idx", "屏幕", "屏幕idx", "Δ"))
rows = []
for exp, gar in PAIRS:
    ie = IDX.get(exp, -1)
    ig = IDX.get(gar, -1)
    d = ig - ie if (ie >= 0 and ig >= 0) else None
    rows.append((exp, ie, gar, ig, d))
    print("  %-6s %-8d %-6s %-8d %s" % (exp, ie, gar, ig, ("%+d" % d) if d is not None else "?"))
print()

print("=== 检验：Δ 是否与期望索引的「区段」相关 ===")
# 按期望索引排序，看 Δ 是否分段变化
srt = sorted([r for r in rows if r[4] is not None], key=lambda r: r[1])
print("  %-6s %-8s %-8s %s" % ("期望", "期望idx", "Δ", "屏幕字"))
for exp, ie, gar, ig, d in srt:
    print("  %-6s %-8d %+8d %s" % (exp, ie, d, gar))
print()

# 另一假设：屏幕索引 = 期望索引 的某种「字节序」变换
print("=== 检验字节序假设 ===")
print("  %-6s %-8s %-6s %-8s %-10s %-10s %s" %
      ("期望", "idx", "屏幕", "idx", "idx字节交换", "idx高地位", "匹配"))
for exp, ie, gar, ig, d in srt[:12]:
    swap = ((ie & 0xFF) << 8) | ((ie >> 8) & 0xFF)
    hi = ie >> 8
    lo = ie & 0xFF
    print("  %-6s %-8d %-6s %-8d %-10d %-10d %s" %
          (exp, ie, gar, ig, swap, (lo << 8) | hi, "✓" if swap == ig else ""))
print()

# 检查是否「屏幕索引」对应 charlist 里某个固定区间的字
print("=== 屏幕字索引的分布 ===")
gidx = sorted([r[3] for r in rows if r[3] >= 0])
print("  %s" % gidx)
eidx = sorted([r[1] for r in rows if r[1] >= 0])
print("  期望索引: %s" % eidx)
print()

# 关键：是否 屏幕索引 ≈ 期望索引 * k（线性）？
print("=== 线性拟合检验 ===")
import statistics
ratios = [(r[3] / r[1]) for r in rows if r[1] > 0 and r[3] >= 0]
print("  比值: %s" % ["%.3f" % x for x in ratios])
print("  均值 %.3f 标准差 %.3f" % (statistics.mean(ratios), statistics.pstdev(ratios)))
