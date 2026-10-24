# 对比两次的显示：
#  A) 写 UTF-8  ->  屏幕: đ³ āĐ□e□□ē¡
#  B) 写 GBK    ->  屏幕: ¹ º Âð · ² û¿ É ÕÖ» ñ µÃ ª ñ ¹ £ Õ ë
cases = {
 "A_UTF8_音效选项": ("音效选项", "utf-8"),
 "B_GBK_音效选项":  ("音效选项", "gbk"),
 "A_UTF8_善用掩体可以减少受伤": ("善用掩体可以减少受伤", "utf-8"),
 "B_GBK_善用掩体可以减少受伤":  ("善用掩体可以减少受伤", "gbk"),
}
import unicodedata
for k,(t,enc) in cases.items():
    b = t.encode(enc)
    print("=== %s ===" % k)
    print("  字节: %s" % b.hex(" "))
    # 假设引擎按 latin-1 逐字节 -> 码点
    latin = [x for x in b]
    print("  按 latin-1 解出的码点: %s" % latin[:14])
    print("  对应字符: %r" % "".join(chr(x) for x in latin[:14]))
    print()
