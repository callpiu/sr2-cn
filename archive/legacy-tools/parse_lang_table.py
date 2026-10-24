# -*- coding: utf-8 -*-
"""解析 SR2_pc.exe 里的语言代码表与资源名模板。

已知
    @0xA26024  "static_%s.le_strings"
    @0xA26070  "charlist_%s.txt"
    @0x9E1810  "forcelang_ch"

目标
    找出游戏支持的【完整语言代码表】，以及 forcelang_ch -> 什么代码。
    如果 ch 映射到的代码不是 "CH"，那游戏就会去找 static_XX.le_strings，
    而 patch.vpp_pc 里只有 static_CH —— 这就解释了「改了没用」！
"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()

# 1) 语言代码表区域
A, B = 0xA25F80, 0xA26120
print("=== 0x%X..0x%X 区域（字符串 + 代码）===" % (A, B))
seg = d[A:B]
for o in range(0, len(seg), 16):
    chunk = seg[o:o + 16]
    print("  %08X  %s  |%s|" % (A + o,
                               " ".join("%02X" % x for x in chunk),
                               "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)))
print()

# 2) 提取所有 NUL 结尾短字符串及偏移
print("=== 提取的短字符串（含偏移）===")
i = A
while i < B:
    if 32 <= d[i] < 127:
        j = i
        while j < B and 32 <= d[j] < 127:
            j += 1
        s = d[i:j].decode("latin1")
        if 1 <= len(s) <= 40:
            print("  0x%06X  %-30s (len %d)" % (i, s, len(s)))
        i = j
    else:
        i += 1
print()

# 3) forcelang 相关字符串
print("=== forcelang 相关 ===")
for pat in (b"forcelang", b"forceLang", b"ForceLang"):
    i = 0
    while True:
        k = d.find(pat, i)
        if k < 0:
            break
        j = k
        while j < len(d) and 32 <= d[j] < 127:
            j += 1
        print("  0x%06X  %s" % (k, d[k:j].decode("latin1")))
        i = k + 1
print()

# 4) 语言代码附近（0xA25FCE 之前）找代码数组
print("=== 0xA25F90..0xA26010 逐字节（找语言代码数组）===")
seg = d[0xA25F90:0xA26010]
# 尝试按 3 字节步进解析（2 字符 + NUL）
for o in range(0, len(seg) - 3, 3):
    trio = seg[o:o + 3]
    if trio[2] == 0 and 32 <= trio[0] < 127 and 32 <= trio[1] < 127:
        print("  0x%06X  %r" % (0xA25F90 + o, trio[:2].decode("latin1")))
print()
print("=== 按 4 字节步进 ===")
for o in range(0, len(seg) - 4, 4):
    quad = seg[o:o + 4]
    if quad[2] == 0 and quad[3] == 0 and 32 <= quad[0] < 127 and 32 <= quad[1] < 127:
        print("  0x%06X  %r" % (0xA25F90 + o, quad[:2].decode("latin1")))
