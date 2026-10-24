# -*- coding: utf-8 -*-
# 方案 B 决定性一步：算出 22 组的 Δ = E(c) - B.index(c)，看偏移规律
# 硬事实：
#   图集第 k 格 = B[k+5]   (OFFSET=5, 逐格视觉验证)
#   引擎取格 E(c) -> 屏幕显示 B[E(c)+5]
#   => E(c) = B.index(显示字) - 5
import re, sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
raw = f.v.read(f.cl_entry).decode("utf-8")
lines = raw.split("\r\n")
B = []
for L in lines:
    s = L.strip()
    if s.startswith("//") or not s:
        continue
    if s.startswith("count="):
        continue
    for tok in s.split():
        if tok.isdigit():
            B.append(chr(int(tok)))
print("B 长度 =", len(B))

# 22 组：源字 -> 实际显示字（用户读数 100% 可靠）
pairs = list(zip("你好兄弟需要保护", "任璨偶巧位雄衡伪该")) + \
        list(zip("正要去进行交易保护他们避免受到攻击", "校勾远貌乱携伪该亡位通像匪冰挺拮"))
print("对照组数 =", len(pairs))

idx = {c: i for i, c in enumerate(B)}
rows = []
for src, disp in pairs:
    if src not in idx:
        print("  !! 源字不在 B:", src); continue
    if disp not in idx:
        print("  !! 显示字不在 B:", disp); continue
    bi, di = idx[src], idx[disp]
    E = di - 5
    rows.append((src, ord(src), bi, disp, ord(disp), di, E, E - bi))

print()
print("%-4s %-7s %-6s %-5s %-7s %-6s %-6s %s" % ("源","码点","B序","显示","码点","B序","E(c)","Δ"))
for r in sorted(rows, key=lambda x: x[2]):
    print("%-4s U+%04X %-6d %-5s U+%04X %-6d %-6d %+d" %
          (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))

print()
print("=== Δ 分布 ===")
ds = [r[7] for r in rows]
print("Δ 值:", sorted(ds))
print("Δ 唯一值数 =", len(set(ds)))
print("Δ 全为负?", all(d < 0 for d in ds), " 全为正?", all(d > 0 for d in ds))

print()
print("=== 假设检验：Δ 是否 = -(B.index(c) 之前被剔除的字符数) ===")
print("即：引擎表 M = B 去掉若干字符，E(c) = c 在 M 中的名次")
print("若成立，则 E(c) <= B.index(c)，且差值即 B 前 index 个中被剔除的数量")
# 检查 E 是否单调于 B.index
srt = sorted(rows, key=lambda x: x[2])
print("按 B 序排序后 E 序列:", [r[6] for r in srt])
mono = all(srt[i][6] < srt[i+1][6] for i in range(len(srt)-1))
print("E 是否随 B 序严格递增（M 是 B 的子序列的必要条件）:", mono)

# 若 M 是 B 的子序列：B[p(E(c))] == c，p 严格递增
print()
print("=== 子序列约束 ===")
pts = sorted((r[6], r[2]) for r in rows)   # (E, B序)
ok = all(pts[i][1] < pts[i+1][1] for i in range(len(pts)-1))
print("B 序是否随 E 严格递增（即 p 递增）:", ok)
print("(E, B序) 对:", pts)

# 检查 p(j)-j 是否单调（若引擎只在前端剔字符则递减/恒定）
print()
print("p(j)-j 序列:", [b - e for e, b in pts])
gaps = [pts[i+1][0] - pts[i][0] for i in range(len(pts)-1)]
print("相邻 E 间隔:", gaps)
