# -*- coding: utf-8 -*-
# 决定性实验：图集 fnt_chinese.g_peg_pc = 4194304 字节，但 DXT3 2048x2048 只需 2097152
# => 有 2097152 字节额外数据，可能内嵌字符表
import sys, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
a = f.atlas
print("图集大小 =", len(a), " DXT3 2048x2048 需要 =", 2048 * 2048 // 16 * 8)

# 找 DXT3 数据起始（图集可能前面有 peg 头）
# 先看文件头
print("\n=== 前 64 字节 ===")
print(a[:64].hex(" "))

# 若前 2MB 是元数据/另一张图，找其中的码点序列
print("\n=== 在前 2MB 里搜 2795 个码点的 u16 序列 ===")
B = f.charlist
head = a[:2097152]
# 尝试 LE / BE
for endian in ("<", ">"):
    pat = b"".join(struct.pack(endian + "H", cp) for cp in B[:200])
    pos = head.find(pat)
    print("  %s-endian 前 200 个码点序列: %s" % (endian, "找到 @0x%X" % pos if pos >= 0 else "未找到"))

# 也搜单个码点：U+4EEC(们) 的位置
for cp in (0x4EEC, 0x62A4, 0x4F4D, 0x8BE5):
    for endian in ("<", ">"):
        b = struct.pack(endian + "H", cp)
        pos = [m.start() for m in re.finditer(re.escape(b), head)][:3]
        if pos:
            print("  U+%04X (%s-endian) 出现于 %s" % (cp, endian, [hex(p) for p in pos]))

# 整个文件都搜一遍
print("\n=== 全文件搜 们(U+4EEC)/护(U+62A4) ===")
for cp in (0x4EEC, 0x62A4):
    for endian in ("<", ">"):
        b = struct.pack(endian + "H", cp)
        pos = [m.start() for m in re.finditer(re.escape(b), a)][:5]
        if pos:
            print("  U+%04X (%s-endian): %s" % (cp, endian, [hex(p) for p in pos]))

# 检查 peg 头结构：常见 peg 有 'GACT'/'GPTV' 等 magic
print("\n=== 查找 peg magic ===")
for magic in (b"GACT", b"GPTV", b"GATG", b"PEGC", b"pegp"):
    p = a.find(magic)
    print("  %s: %s" % (magic, hex(p) if p >= 0 else "无"))
