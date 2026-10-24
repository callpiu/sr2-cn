# -*- coding: utf-8 -*-
# 检验「取格 = floor(累计字宽 / 31)」假设
# 字宽取自 vf3 的 16 字节记录第 1 个 u16 字段
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
COMMON = r"G:/SteamLibrary/steamapps/common/Saints Row 2/common.vpp_pc"
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}

SRC = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"
DISP = "任璨偶巧们校衡勾远藐乱携伪该亡们通像匪冰挺拮"
Es = [bidx[d] - 5 for d in DISP]
print("E 序列:", Es)

# fnt_chinese 的字宽（记录第1个u16）
N = f.N
UOFF = f.UOFF
widths = []
for i in range(N):
    r = struct.unpack_from("<8H", f.vf3, 0xD0 + i * 16)
    widths.append(r[0])
print("\nfnt_chinese 字宽样例:", widths[:10], " 唯一值数:", len(set(widths)))

# 假设：x_k = sum(width[c] for c in SRC[:k])，取格 = x_k // 31
for div in (31, 30, 32, 22, 25):
    x = 0
    pred = []
    for c in SRC:
        pred.append(x // div)
        x += widths[bidx[c]] if c in bidx else 0
    hit = sum(1 for p, e in zip(pred, Es) if p == e)
    print("  宽度累计/%d : 命中 %d/%d" % (div, hit, len(Es)))

# 反向：若取格 = 累计槽位相关
print("\n=== 累计槽位 mod 某数 ===")
acc = 0
pred = []
for c in SRC:
    pred.append(acc % 2795)
    acc += (bidx[c] + 32) if c in bidx else 0
hit = sum(1 for p, e in zip(pred, Es) if p == e)
print("  累计槽位 mod 2795: 命中 %d/%d" % (hit, len(Es)))
print("  预测:", pred[:12])
print("  实际:", Es[:12])

# 检验：E 是否 = (B.index(c) * k) mod 2795
print("\n=== 线性/乘法变换 ===")
for k in range(2, 40):
    hit = sum(1 for c, e in zip(SRC, Es)
              if c in bidx and (bidx[c] * k) % 2795 == e)
    if hit >= 4:
        print("  E = (B序 * %d) mod 2795 : 命中 %d/%d" % (k, hit, len(SRC)))

# 检验：E 是否 = hash(c) 的低位
print("\n=== E 与源字码点的关系 ===")
for c, e in list(zip(SRC, Es))[:12]:
    print("  %s(U+%04X) B序=%-5d E=%-5d E-B序=%+d  E与码点关系: E%%%d=%d" % (
        c, ord(c), bidx.get(c, -1), e, e - bidx.get(c, 0), ord(c), e % max(ord(c), 1)))
