# -*- coding: utf-8 -*-
"""分析 forcelang_ch 的处理逻辑：ch 在语言代码表里吗？

发现
    @0x9E1810  "forcelang_ch"
    @0xA25FB8.. 语言代码表: ru pl dk nl fr de it es en / RU SK CZ DK SE NL JP US
    ★ 表里没有 "CH"！

如果游戏解析 forcelang_XX 后在表里查不到，会 fallback 到系统语言或默认语言。
那么 static_CH.le_strings 就【不会被加载】—— 但用户明明看到了中文！

=> 说明有另一条路径在提供中文。需要查清楚。
"""
import os, struct, re

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()

# 1) forcelang_* 全部变体
print("=== exe 里所有 'forcelang' 字符串 ===")
i = 0
seen = set()
while True:
    k = d.find(b"forcelang", i)
    if k < 0:
        break
    j = k
    while j < len(d) and 32 <= d[j] < 127:
        j += 1
    s = d[k:j].decode("latin1")
    if s not in seen:
        seen.add(s)
        print("  0x%06X  %r" % (k, s))
    i = k + 1
print()

# 2) 看 0x9E1760..0x9E1900（语言代码/forcelang 区域）
A, B = 0x9E1760, 0x9E1900
print("=== 0x%X..0x%X ===" % (A, B))
seg = d[A:B]
for o in range(0, len(seg), 16):
    ch = seg[o:o + 16]
    print("  %08X  %s  |%s|" % (A + o,
                               " ".join("%02X" % x for x in ch),
                               "".join(chr(x) if 32 <= x < 127 else "." for x in ch)))
print()

# 3) 提取该区域所有可打印字符串
print("=== 该区域的字符串 ===")
i = A
while i < B:
    if 32 <= d[i] < 127:
        j = i
        while j < B and 32 <= d[j] < 127:
            j += 1
        s = d[i:j].decode("latin1")
        if len(s) >= 2:
            print("  0x%06X  %r" % (i, s))
        i = j
    else:
        i += 1
print()

# 4) 查 'ch' 作为独立字符串出现的位置
print("=== 'ch' 作为独立 NUL 结尾字符串 ===")
for m in re.finditer(rb"(?<![A-Za-z0-9])ch\x00", d):
    k = m.start()
    print("  0x%06X" % k)
print()

# 5) 语言代码表的完整字节（含可能被忽略的）
print("=== 0xA25FB0..0xA26000 的原始字节 ===")
seg = d[0xA25FB0:0xA26000]
for o in range(0, len(seg), 16):
    print("  %08X  %s  |%s|" % (0xA25FB0 + o,
                               " ".join("%02X" % x for x in seg[o:o + 16]),
                               "".join(chr(x) if 32 <= x < 127 else "." for x in seg[o:o + 16])))
