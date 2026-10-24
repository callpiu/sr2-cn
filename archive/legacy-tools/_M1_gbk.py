# -*- coding: utf-8 -*-
"""假说：内存里存的是 GBK 字节，被当成 UTF-16 读 → 乱码。
验证：把乱码字当 GBK 编码，看能否还原正确字。
"""
pairs = [
    ('任','你'), ('璨','的'), ('偶','弟'), ('巧','兄'),
    ('位','们'), ('雄','需'), ('衡','要'), ('伪','保'), ('该','护'),
]
print("=== 逐字对照 ===")
for bad, good in pairs:
    print("  %s(U+%04X) vs %s(U+%04X) | GBK(乱码)=%s GBK(正确)=%s" % (
        bad, ord(bad), good, ord(good),
        bad.encode('gbk','replace').hex().upper(),
        good.encode('gbk','replace').hex().upper()))
print()
print("=== 假说1: UTF-8 被当 GBK 读 ===")
s = "你的弟兄们需要你的保护"
print("  正确文本 UTF-8 =", s.encode('utf-8').hex().upper())
print("  UTF-8 用 GBK 解码 =", s.encode('utf-8').decode('gbk','replace'))
print()
print("=== 假说2: GBK 被当 UTF-16LE 读 ===")
g = s.encode('gbk')
print("  GBK 字节 =", g.hex().upper())
print("  GBK 当 UTF-16LE 解码 =", g.decode('utf-16-le','replace'))
print("  GBK 当 UTF-16BE 解码 =", g.decode('utf-16-be','replace'))
print()
print("=== 假说3: charlist 索引错位 (slot-32 vs slot) ===")
# 乱码字 任=U+4EFB, 正确 你=U+4F60
print("  乱码屏幕: 任璨偶巧位雄衡伪该")
print("  正确文本: 你的弟兄们需要保护")
print()
print("=== 假说4: 用错 charlist（中文表按别的语言表解）===")
for ch in "任璨偶巧位":
    print("  %s U+%04X" % (ch, ord(ch)))
