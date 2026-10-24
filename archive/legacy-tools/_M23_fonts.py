# -*- coding: utf-8 -*-
# 决定性检验：HUD 字幕字体 thin_overlay -> fnt_body_n 的 vf3 是什么？
# 若 N=224（英文表），则字幕取格 357/2337 会越界读取 -> 异常取格的另一种解释
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)


def vf3info(name):
    e = cn.find(name, "vf3_pc")
    if not e:
        return None
    d = cn.read(e)
    if len(d) < 12 or d[:4] != b"VFNT":
        return None
    N, = struct.unpack_from("<I", d, 8)
    return d, N


for name in ("fnt_chinese", "fnt_body_n", "fnt_body_s", "fnt_head_n", "fnt_bodyital_n"):
    r = vf3info(name)
    if not r:
        print("%-16s 未找到或不合法" % name)
        continue
    d, N = r
    UOFF = 0xD0 + N * 16
    VOFF = UOFF + N * 4
    print("\n=== %s.vf3_pc (%d B) N=%d ===" % (name, len(d), N))
    print("  记录区 0xD0..0x%X   U表@0x%X  V表@0x%X" % (UOFF, UOFF, VOFF))
    print("  V 表项数 = %d（N=%d，缺%d）" % ((len(d) - VOFF) // 4, N, N - (len(d) - VOFF) // 4))
    # 内嵌串
    for off in (0x28, 0x68):
        if off < len(d):
            end = d.find(b"\x00", off)
            s = d[off:end if end > 0 else off + 40]
            if s and all(32 <= b < 127 for b in s):
                print("  内嵌串@0x%X: %s" % (off, s.decode()))
    # 关键索引的 U/V
    if N >= 2400:
        for label, k in (("们应有的格327", 327), ("位/们的落点357", 357),
                         ("护应有的格1185", 1185), ("该/护的落点2337", 2337)):
            if k < N and UOFF + k * 4 + 4 <= len(d):
                u, = struct.unpack_from("<i", d, UOFF + k * 4)
                v, = struct.unpack_from("<i", d, VOFF + k * 4)
                print("  %-16s U=%-6d V=%-6d -> 图集第%d格(行%d,列%d)" % (
                    label, u, v, k, v // 31, u // 31))
    else:
        print("  ★ N=%d < 2400：字幕取格 357/2337 会**越界**！" % N)
        # 看 N 之后的内存内容（越界区）
        print("  0xD0+N*16 之后的 U 表前几项:", struct.unpack_from("<8i", d, UOFF)[:8] if UOFF + 32 <= len(d) else "N/A")

# 对比 fnt_chinese 与 fnt_body_n 是否同一张表
a = vf3info("fnt_chinese")
b = vf3info("fnt_body_n")
if a and b:
    print("\n=== fnt_chinese vs fnt_body_n ===")
    print("  大小: %d vs %d   相同=%s" % (len(a[0]), len(b[0]), a[0] == b[0]))
