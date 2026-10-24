# -*- coding: utf-8 -*-
"""找 SR2_pc.exe 里加载文本表的代码。

线索
    - patch.vpp_pc 含正确文本，但游戏不读
    - 说明游戏从【别处】加载文本（可能是内嵌/缓存/不同的资源名）

搜索目标
    1. "charlist" / "static_" / "le_strings" 等资源名字符串（游戏用它拼资源名）
    2. 字符表加载函数（compress_char 的邻居）
"""
import os, struct, re

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
print("SR2_pc.exe %d 字节" % len(d))
print()

KEYS = [b"charlist", b"static_", b"le_strings", b"voice_script", b"platform_pc",
        b"platform_PC", b"strings", b"localize", b"Localize", b"get_localized",
        b"loadstrings", b"load_strings", b"lang", b"language"]

print("=== 关键字符串在 exe 里的位置 ===")
for k in KEYS:
    hits = []
    i = 0
    while True:
        j = d.find(k, i)
        if j < 0:
            break
        hits.append(j)
        i = j + 1
        if len(hits) > 8:
            break
    if hits:
        print("  %-18s %d 处: %s" % (k.decode("latin1"), len(hits), ["0x%X" % h for h in hits[:6]]))
    else:
        print("  %-18s 未找到" % k.decode("latin1"))
print()

# 看 le_strings 附近的字符串
for k in (b"le_strings", b"charlist"):
    i = d.find(k)
    if i < 0:
        continue
    print("=== %s 附近 (0x%X) ===" % (k.decode(), i))
    seg = d[max(0, i - 96):i + 96]
    for o in range(0, len(seg), 16):
        chunk = seg[o:o + 16]
        print("  %08X  %s  |%s|" % (max(0, i - 96) + o,
                                   " ".join("%02X" % x for x in chunk),
                                   "".join(chr(x) if 32 <= x < 127 else "." for x in chunk)))
    print()

# 找中文相关的资源名（可能是 base name）
print("=== 含 '_CH' / 'CH' 的短字符串 ===")
RD_RAW, RD_SZ = 0x9B8000, 0xC8000
seg = d[RD_RAW:RD_RAW + RD_SZ]
for s in re.findall(rb"[\x20-\x7E]{3,40}", seg):
    t = s.decode("latin1")
    if t.endswith("_CH") or t.endswith("_ch") or t in ("CH", "ch", "zh", "ZH"):
        off = RD_RAW + seg.find(s)
        print("  0x%06X  %s" % (off, t))
