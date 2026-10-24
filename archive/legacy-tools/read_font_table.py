"""读 SR2_pc.exe 里的字体别名注册表与字符串池。

交接文档 §7.5 给出的地址（无 ASLR，VA == 文件偏移）：
    0x9e0fc0  字体字符串池
    0x11d612~0x11d679  别名注册
    0x11d290  语言→字体 switch 表

目标
    确认 thin_overlay（字幕用的别名）到底绑定哪两个字体资源，
    以及这些字体是不是 ASCII-only（fnt_body_n / fnt_body_s）。
"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
EXE = os.path.join(G, "SR2_pc.exe")
d = open(EXE, "rb").read()
print("SR2_pc.exe %d 字节" % len(d))
print()

# 1) 字符串池
POOL = 0x9E0FC0
print("=== 字符串池 @0x%X（前 320 字节）===" % POOL)
seg = d[POOL:POOL + 320]
# 按 \0 切分
parts = seg.split(b"\x00")
out = []
for i, p in enumerate(parts):
    txt = p.decode("latin1")
    out.append(txt)
print("  片段: %s" % " | ".join(t for t in out if t)[:400])
print()
# 找关键名字
for name in (b"thin", b"thin_overlay", b"header_n", b"fnt_body_n", b"fnt_body_s",
             b"fnt_chinese", b"fnt_korea", b"fnt_cz", b"jap", b"bodyital_overlay"):
    i = d.find(name)
    print("  %-20s 首次出现 @0x%X" % (name.decode(), i))
print()

# 2) 别名注册区
A = 0x11D612
B = 0x11D679
print("=== 别名注册区 0x%X..0x%X (%d 字节) ===" % (A, B, B - A))
seg = d[A:B + 16]
for i in range(0, len(seg), 16):
    hx = " ".join("%02X" % x for x in seg[i:i + 16])
    print("  %08X  %s" % (A + i, hx))
print()

# 3) 语言→字体 switch 表
S = 0x11D290
print("=== 语言→字体 switch 表 @0x%X（96 字节）===" % S)
seg = d[S:S + 96]
for i in range(0, 96, 16):
    hx = " ".join("%02X" % x for x in seg[i:i + 16])
    # 尝试解成 dword
    vals = struct.unpack_from("<4I", seg, i)
    print("  %08X  %-47s  %s" % (S + i, hx, " ".join("%08X" % v for v in vals)))
