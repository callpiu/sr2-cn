# -*- coding: utf-8 -*-
"""生成 hook 用的精确匹配表。

原理
    游戏在内存里把 static_CH 的槽位解码成 Unicode 字符串。
    槽位 S 对应的 Unicode = 某个字符（由引擎决定）。
    我从截图知道了「实际显示的乱码字」，但不知道引擎内部的槽位->字符映射。

    不过！我可以直接用【乱码字符本身的 Unicode】作为匹配键：
    屏幕上显示「使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋」，
    那么在内存里，这个字符串的 Unicode 编码就是这 22 个字的 UTF-16LE。
    不管引擎内部怎么映射，只要它在屏幕上显示这些字，
    它传给渲染函数的字符串里就含这些 Unicode 码点。

    所以匹配键 = 乱码字符串的 UTF-16LE 字节。

本脚本输出
    · 两条字幕的乱码字符串的 UTF-16LE / UTF-8 字节
    · 可直接粘进 C++ 源码的转义序列
"""
import os
import sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
import struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 用户报告的两条乱码（第 1 条来自面板那次截图，第 2 条来自最近）
GARBLED_1 = "使發光彈借歷復使發俱誘"          # 较早的截图（短）
GARBLED_2 = "使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋"

# static_CH 的槽位
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
      if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)

RECS = {}
for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
    id1, id2 = struct.unpack_from("<HH", d, off)
    h = (id1 << 16) | id2
    if h in (0x84F287ED, 0x10AF1E62):
        u, _ = read_units(d, off + 8)
        RECS[h] = ([x for x, _ in u], "".join(S.get(x, "·") for x, _ in u))

print("=" * 76)
print("static_CH 里的两条字幕（正确繁中）")
print("=" * 76)
for h, (slots, txt) in sorted(RECS.items()):
    print("  0x%08X  %r" % (h, txt))
    print("           槽位: %s" % slots)
print()

print("=" * 76)
print("用户截图看到的乱码")
print("=" * 76)
for i, g in enumerate((GARBLED_1, GARBLED_2), 1):
    print("  [%d] %r  (%d 字)" % (i, g, len(g)))
    print("      UTF-16LE: %s" % g.encode("utf-16-le").hex(" "))
    print("      UTF-8   : %s" % g.encode("utf-8").hex(" "))
    print()


def cpp_escape(s, enc):
    b = s.encode(enc)
    out = []
    for ch in b:
        out.append("\\x%02X" % ch)
    return "".join(out)


print("=" * 76)
print("可直接用于 C++ 的匹配键")
print("=" * 76)
for i, g in enumerate((GARBLED_1, GARBLED_2), 1):
    print("  // 乱码 %d" % i)
    print('  static const wchar_t kBad%d[] = L"%s";' % (i, g))
    print('  // UTF-16LE: "%s"' % cpp_escape(g, "utf-16-le"))
    print()

print("=" * 76)
print("要替换成的正确繁中（同样需要引擎能渲染）")
print("=" * 76)
for h, (slots, txt) in sorted(RECS.items()):
    print("  0x%08X -> %r" % (h, txt))
