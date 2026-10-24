# -*- coding: utf-8 -*-
# 对比两个版本的 SR2_pc.exe：字体表 / 语言表 / 结构差异
import os, struct, hashlib, re

CUR = r"G:/SteamLibrary/steamapps/common/Saints Row 2/SR2_pc.exe"
OLD = r"F:/sr2-cn/SR2_pc.exe.orig"
for p in (CUR, OLD):
    print("%-46s size=%-10d md5=%s" % (os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p),
                                      os.path.getsize(p), hashlib.md5(open(p, "rb").read()).hexdigest()))

a = open(CUR, "rb").read()
b = open(OLD, "rb").read()

# 1) PE 头信息
for tag, d in (("当前", a), ("备份", b)):
    pe = struct.unpack_from("<I", d, 0x3C)[0]
    mach, nsec = struct.unpack_from("<HH", d, pe + 4)
    print("  [%s] PE@0x%X machine=0x%X 节数=%d  时间戳=%s" % (
        tag, pe, mach, nsec, struct.unpack_from("<I", d, pe + 8)[0]))
    for i in range(nsec):
        o = pe + 0x18 + i * 40
        nm = d[o:o + 8].rstrip(b"\x00").decode("ascii", "replace")
        vsz, va, rsz, ro = struct.unpack_from("<IIII", d, o + 8)
        print("       %-8s vsize=%-9d va=0x%X rawsize=%-9d rawoff=0x%X" % (nm, vsz, va, rsz, ro))

# 2) 字体相关字符串位置
KEYS = [b"fnt_chinese", b"fnt_body_n", b"thin_overlay", b"forcelang", b"localize_language",
        b"charlist", b"le_strings", b"font_hudsmall"]
print("\n=== 关键字符串位置 ===")
for k in KEYS:
    pa = [hex(m.start()) for m in re.finditer(re.escape(k), a)][:4]
    pb = [hex(m.start()) for m in re.finditer(re.escape(k), b)][:4]
    print("  %-18s 当前=%s   备份=%s" % (k.decode(), pa, pb))

# 3) 语言 switch 表附近（备份里的 0x11d290 与 0x11d612）
print("\n=== 0x11D280 区域（语言→字体 switch / 别名注册）===")
for tag, d in (("当前", a), ("备份", b)):
    if len(d) <= 0x11D700:
        continue
    print("  [%s] %s" % (tag, d[0x11D2B0:0x11D2E0].hex(" ")))
    print("        别名区 %s" % d[0x11D610:0x11D660].hex(" "))

# 4) 差异区块统计（按 64KB 分块）
print("\n=== 分块差异（每 64KB 一块，列出差异块）===")
CH = 0x10000
n = min(len(a), len(b)) // CH
diff_blocks = []
for i in range(n):
    if a[i * CH:(i + 1) * CH] != b[i * CH:(i + 1) * CH]:
        diff_blocks.append(i)
print("  差异块数 = %d / %d" % (len(diff_blocks), n))
print("  前 40 个: %s" % [hex(x * CH) for x in diff_blocks[:40]])
