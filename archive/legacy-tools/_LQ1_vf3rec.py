# -*- coding: utf-8 -*-
# 决定性实验：vf3 的 16 字节记录里是否含「字符码点」？
# 若记录 i 含 B[i] 的码点，则引擎从 vf3 读字符表 -> 找错字的来源
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
N = f.N
vf3 = f.vf3
B = [chr(c) for c in f.charlist]
print("N =", N, " vf3 大小 =", len(vf3), " UOFF = 0x%X VOFF = 0x%X" % (f.UOFF, f.VOFF))

print("\n=== 前 8 条记录原文（16 字节）===")
for i in range(8):
    r = vf3[0xD0 + i * 16: 0xD0 + (i + 1) * 16]
    print("  [%3d] %s   u16x8=%s" % (i, r.hex(" "),
          struct.unpack_from("<8H", r)))

# 检验：记录 i 的哪个 u16 字段 == B[i] 的码点？
print("\n=== 字段定位：哪个 u16 槽位等于 B[i] 的码点 ===")
hits = [0] * 8
for i in range(N):
    cp = ord(B[i])
    r = struct.unpack_from("<8H", vf3, 0xD0 + i * 16)
    for j in range(8):
        if r[j] == cp:
            hits[j] += 1
print("各 u16 槽位命中数（共 %d 条）:" % N, hits)

# 若某槽位高命中，打印前几条
best = max(range(8), key=lambda j: hits[j])
if hits[best] > N * 0.5:
    print("\n槽位 %d 高命中（%d/%d）—— 前 10 条:" % (best, hits[best], N))
    for i in range(10):
        r = struct.unpack_from("<8H", vf3, 0xD0 + i * 16)
        print("  [%3d] B=%s(U+%04X) 记录=%s" % (i, B[i], ord(B[i]), r))

# 关键：们/护 的记录 vs 位/该 的记录
print("\n=== 关键字的 vf3 记录 ===")
for ch in "你兄弟需要保们位护该":
    i = B.index(ch)
    r = struct.unpack_from("<8H", vf3, 0xD0 + i * 16)
    print("  %s idx=%-5d U+%04X 记录=%s" % (ch, i, ord(ch), r))

# 另一思路：若记录含码点但顺序错位 —— 检查「记录 i 的码点字段」构成什么序列
if hits[best] > N * 0.5:
    seq = [struct.unpack_from("<8H", vf3, 0xD0 + i * 16)[best] for i in range(N)]
    nonmono = [i for i in range(N - 1) if seq[i] >= seq[i + 1]]
    print("\n该字段序列非单调点数 =", len(nonmono), " 前 20:", nonmono[:20])
    print("该字段构成表是否含 们(U+4EEC):", 0x4EEC in seq, "  护(U+62A4):", 0x62A4 in seq)
    for ch in "你兄弟需要保们位护该":
        cp = ord(ch)
        print("  U+%04X(%s) 在该序列中的位置 = %s" % (cp, ch, seq.index(cp) if cp in seq else "不在"))
