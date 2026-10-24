# -*- coding: utf-8 -*-
# 算 8848.0138 每个源字的 E 偏移，找出引擎表 L 与 charlist 的差异规律
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
OFF = 5

SRC = "好了，咱们离开这儿吧……"
DISP = "任璨偶巧们校衡勾远藐乱携"
assert len(SRC) == len(DISP), (len(SRC), len(DISP))

print("%-3s %-8s %-8s %-8s %s" % ("位", "源字", "显示字", "E(实测)", "偏移"))
rows = []
for i, (c, d) in enumerate(zip(SRC, DISP), 1):
    bi = bidx.get(c, -1)
    di = bidx.get(d, -1)
    E = di - OFF
    exp = bi - OFF
    rows.append((i, c, d, E, exp, E - exp))
    print("%-3d %-8s %-8s %-8d %+d  %s" % (i, c, d, E, E - exp,
          "OK" if E == exp else "★"))

print("\n=== 偏移量序列 ===")
print([r[5] for r in rows])

# 假设：E(c) = B.index(c) - 5 + delta(c)。delta 若与 c 的码点相关？
print("\n=== 源字码点与 delta ===")
for i, c, d, E, exp, delta in rows:
    print("  %s(U+%04X) delta=%+d" % (c, ord(c), delta))

# 假设：引擎表 L 按「码点」排序但长度不同？
# 若 L = B 去掉前 k 项，则 E(c) = B.index(c) - k
# 正常 k=5。检验 delta 是否 = 常数
deltas = set(r[5] for r in rows)
print("\ndelta 唯一值:", sorted(deltas))

# 假设：L 是另一个表，E(c) = c 在 L 中的名次
# 已知锚点：们 E=327（正常，B.index(们)-5=327）
# 好 E=331 -> L[331]=好?
print("\n=== 若 L[i]=源字，检查 L 是否 = B[5:] ===")
for i, c, d, E, exp, delta in rows:
    if 0 <= E < len(B):
        print("  L[%d] = %s   B[%d+5]=B[%d]=%s  %s" % (
            E, c, E, E + OFF, B[E + OFF] if E + OFF < len(B) else "?",
            "一致" if E + OFF < len(B) and B[E + OFF] == c else "★不一致"))
