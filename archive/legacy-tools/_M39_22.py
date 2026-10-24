# -*- coding: utf-8 -*-
# 逐字验证 22 字句：你的弟兄们要出去谈几笔生意，保护他们免遭袭击
# 测试各种偏移模型
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}

SRC = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"
DISP = "任璨偶巧们校衡勾远藐乱携伪该亡们通像匪冰挺拮"
print("源 %d 字，显示 %d 字" % (len(SRC), len(DISP)))
assert len(SRC) == len(DISP)

print("\n=== 逐字：源 -> 显示，E(实测) vs 应有 E ===")
for i, (c, d) in enumerate(zip(SRC, DISP), 1):
    bi, di = bidx.get(c, -1), bidx.get(d, -1)
    E = di - 5
    exp = bi - 5
    print("  %2d %s(%-4d) -> %s(%-4d)  E=%-5d 应有=%-5d delta=%+d %s" % (
        i, c, bi, d, di, E, exp, E - exp, "OK" if E == exp else "★"))

# 模型1：显示 = B[槽位-5]，槽位 = B.index(c)+32  => B[B.index(c)+27]  已试 0
# 模型2：显示 = B[槽位+5]，槽位 = B.index(c)+32  => B[B.index(c)+37]
# 模型3：显示 = B[B.index(c) + D] 全扫
print("\n=== 全扫 D ===")
best = []
for D in range(-80, 81):
    hit = sum(1 for c, d in zip(SRC, DISP)
              if c in bidx and 0 <= bidx[c] + D < len(B) and B[bidx[c] + D] == d)
    if hit >= 3:
        best.append((hit, D))
for hit, D in sorted(best, reverse=True)[:10]:
    print("  D=%+d 命中 %d/%d" % (D, hit, len(SRC)))
if not best:
    print("  无任何 D 命中 >=3")

# 关键：检查「护」在两个句子里的 E
print("\n=== 「护」在两句中的表现 ===")
print("  句1 [84F2.87ED] 你的弟兄们需要你的保护 -> 护 显示「该」(E=2337)")
print("  句2 [10AF.1E62] ...保护他们... -> 护 显示「们」(E=327)")
print("  => 同一字不同 E => E 依赖上下文（非纯字符函数）")

# 若 E 依赖位置：检验 E 是否 = 前一个字的 E + 某个量
print("\n=== E 序列与相邻差 ===")
Es = [bidx[d] - 5 for d in DISP]
print("  E:", Es)
print("  相邻差:", [Es[i+1] - Es[i] for i in range(len(Es)-1)])
