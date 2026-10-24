# -*- coding: utf-8 -*-
"""搜索 ACT_HELI 等字符串 ID 的位置。

用户信息：任务 xtbl / 场景脚本只写字符串 ID（如 ACT_HELI_CHOPLIFTER_START_MESSAGE）
引擎拿 ID 去内存里的 le_strings 查表

如果 ID 在 exe 或 VPP 里，那查表逻辑就在那里。
"""
import os
import re
import sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

print("=" * 76)
print("1. exe / dll 里的 ACT_ / 字符串 ID 形式")
print("=" * 76)
for fn in ("SR2_pc.exe", "DFEngine.dll"):
    p = os.path.join(G, fn)
    d = open(p, "rb").read()
    print("--- %s (%d 字节) ---" % (fn, len(d)))
    for pat in (rb"ACT_[A-Z0-9_]{3,60}", rb"[A-Z][A-Z0-9_]{8,60}_MESSAGE",
                rb"[A-Z][A-Z0-9_]{8,60}_TEXT", rb"HELI[A-Z0-9_]*"):
        hits = list(re.finditer(pat, d))
        if hits:
            print("  %-32s %d 处" % (pat.decode(), len(hits)))
            for m in hits[:8]:
                print("      0x%06X  %s" % (m.start(), m.group().decode()))
        else:
            print("  %-32s 未找到" % pat.decode())
    print()

print("=" * 76)
print("2. le_strings 表里是否有 ID 字段（不只是 hash）")
print("=" * 76)
v = Vpp(os.path.join(G, "patch.vpp_pc"))
d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)
print("static_CH: %d 字节, buckets=%d count=%d" % (len(d), b, c))
print()
print("文件头 64 字节:")
for o in range(0, 64, 16):
    ch = d[o:o + 16]
    print("  %04X  %s  |%s|" % (o, " ".join("%02X" % x for x in ch),
                                "".join(chr(x) if 32 <= x < 127 else "." for x in ch)))
print()

# 检查 bucket 表之后是否存了 "ID 字符串表"
# 通常 le_strings 结构: magic + ver + buckets + count + bucket offsets + ID 表 + 文本
# 看看 bucket 区域是否有可打印的 ID
print("bucket 偏移表后 512 字节的可打印字符串:")
reg = d[0x1000:0x1400]
import re as _re
for m in _re.finditer(rb"[\x20-\x7E]{4,60}", reg):
    print("  0x%06X  %s" % (0x1000 + m.start(), m.group().decode()))
    if m.start() > 300:
        break

print()
print("=" * 76)
print("3. 全盘搜索 'ACT_HELI' 在所有文件里")
print("=" * 76)
found = 0
for root, dirs, fs in os.walk(G):
    for f in fs:
        p = os.path.join(root, f)
        try:
            if os.path.getsize(p) > 300 * 1024 * 1024:
                continue
            dd = open(p, "rb").read()
        except Exception:
            continue
        for pat in (b"ACT_HELI", b"ACT_HEL"):
            i = dd.find(pat)
            if i >= 0:
                seg = dd[i:i + 80].split(b"\x00")[0]
                print("  ★ %-52s @0x%X  %r" % (os.path.relpath(p, G), i, seg))
                found += 1
                break
print("  命中 %d" % found)
