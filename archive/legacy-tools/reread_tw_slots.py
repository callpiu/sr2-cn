# -*- coding: utf-8 -*-
"""重新读取【繁中 patch.vpp_pc】里活动字幕的真实槽位，并精确解码。

用户看到的乱码（繁中环境）:
    使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋

本脚本
    1. 直接读 patch.vpp_pc 的 static_CH，找 hash 0x84F287ED / 0x10AF1E62
    2. 打印原始槽位 + 用 charlist_CH 解码
    3. 逐字建立「槽位 -> 屏幕字」的对照表
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62

v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
print("charlist_CH: %d 项" % len(cn))
print()

d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)
print("static_CH: %d 字节, buckets=%d count=%d" % (len(d), b, c))
print()

for h_target in (H1, H2):
    print("=" * 70)
    print("hash 0x%08X" % h_target)
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        id1, id2 = struct.unpack_from("<HH", d, off)
        if ((id1 << 16) | id2) != h_target:
            continue
        u, _ = read_units(d, off + 8)
        vals = [x for x, _ in u]
        txt = "".join(S.get(x, "·") for x in vals)
        print("  记录 @%d, %d 槽位" % (off, len(vals)))
        print("  槽位: %s" % vals)
        print("  解码: %s" % txt)
        print()
        # 逐槽位：槽位值 / 槽位-0x20 / 期望字
        cjk = [(i, x) for i, x in enumerate(vals) if x > 0x100]
        print("  CJK 槽位 (%d 个):" % len(cjk))
        print("    %-4s %-8s %-6s %-6s %s" % ("位", "槽位值", "-0x20", "索引", "字"))
        for i, x in cjk:
            print("    %-4d %-8d %-6d %-6d %s" % (i, x, x - 0x20, x - 0x20, S.get(x, "?")))
        print()
print()
print("=== 用户报告的乱码 ===")
GARBLED = "使發光彈借步復友途螢交星點俱誘仙遞全句剝放擋"
print("  %s (%d 字)" % (GARBLED, len(GARBLED)))
IDX = {chr(cp): i for i, cp in enumerate(cn)}
print("  各字在 charlist_CH 的索引:")
for ch in GARBLED:
    print("    %s -> %d" % (ch, IDX.get(ch, -1)))
