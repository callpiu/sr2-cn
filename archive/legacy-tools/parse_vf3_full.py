# -*- coding: utf-8 -*-
"""解析 fnt_chinese.vf3_pc 的完整结构，找「槽位 -> glyph」的索引表。

已知
    槽位 [437,994,390] -> 屏幕显示 使發光彈
    charlist_CH[405] = 兄  (槽位-0x20)
    但屏幕显示的是别的字 -> 字形索引表 != charlist_CH 顺序

vf3 结构（交接文档 §2.1）
    +0x00  magic?
    +0x04  ver = 2
    +0x08  N = 2838
    +0x0C  firstascii = 32
    +0x10  W
    +0x14  H
    +0x16  RenderH
    +0x18  BasOff
    +0x1C  CharSpacing
    +0x20  KernPairs
    +0x24  VertOff
    +0x28  PegName[64]
    +0x68  BitmapName[64]
    +0xA8  ?
    0xD0   FontCharacter[N]   (16 B each)
    0xD0+N*16   U[N] (i32)
    ...         V[N] (i32)
"""
import os
import struct
import sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

with LightVpp(os.path.join(G, "patch.vpp_pc")) as v:
    vf3 = None
    for e in v.entries():
        if v.name(e) == "fnt_chinese" and v.ext(e) == "vf3_pc":
            vf3 = v.read(e)
            break

print("fnt_chinese.vf3_pc: %d 字节" % len(vf3))
print()

# 头部
N, = struct.unpack_from("<i", vf3, 0x08)
ver, = struct.unpack_from("<i", vf3, 0x04)
fa, = struct.unpack_from("<i", vf3, 0x0C)
W, = struct.unpack_from("<i", vf3, 0x10)
H, = struct.unpack_from("<h", vf3, 0x14)
RH, = struct.unpack_from("<h", vf3, 0x16)
cs, = struct.unpack_from("<h", vf3, 0x1C)
kp, = struct.unpack_from("<i", vf3, 0x20)
print("  ver=%d N=%d firstascii=%d W=%d H=%d RenderH=%d CharSpacing=%d KernPairs=%d" %
      (ver, N, fa, W, H, RH, cs, kp))
print("  PegName = %r" % vf3[0x28:0x68].rstrip(b"\x00"))
print("  Bitmap = %r" % vf3[0x68:0xA8].rstrip(b"\x00"))
print()

BASE = 0xD0
rec_size = 16
recs_end = BASE + N * rec_size
print("  记录区 0x%X .. 0x%X (%d 条 × %d 字节)" % (BASE, recs_end, N, rec_size))
U_end = recs_end + N * 4
V_end = U_end + N * 4
print("  U 表   0x%X .. 0x%X" % (recs_end, U_end))
print("  V 表   0x%X .. 0x%X   (文件总长 %d)" % (U_end, V_end, len(vf3)))
print("  尾部剩余: %d 字节" % (len(vf3) - V_end))
print()

# 检查 N-5（交接文档提到 V 只有 N-5 项）
print("=== 检查 V 表项数 ===")
print("  如果 V 是 N 项: 需要 %d 字节, 实际 %d" % (V_end, len(vf3)))
print("  如果 V 是 N-5 项: 需要 %d 字节" % (U_end + (N - 5) * 4))
print()

# 我们关心的槽位
SLOTS = [437, 994, 390, 1488, 2311, 562]
print("=== 这些槽位在 vf3 里的记录 ===")
print("  %-6s %-8s %-40s %s" % ("槽位", "槽位-0x20", "FontCharacter (16B)", "U/V"))
for s in SLOTS:
    for label, idx in (("槽位", s), ("-0x20", s - 0x20)):
        if 0 <= idx < N:
            o = BASE + idx * rec_size
            rec = struct.unpack_from("<hhhhhhhh", vf3, o)
            uo = recs_end + idx * 4
            u, = struct.unpack_from("<i", vf3, uo)
            v_, = struct.unpack_from("<i", vf3, uo + N * 4)
            print("  %-6s %-8d %-40s U=%-6d V=%d" %
                  (label, idx, rec, u, v_))
    print()

# 找「字符索引表」——可能在 U 表之前或之后
print("=== 搜索 0xD0 之前的区域（可能是 charlist 索引）===")
seg = vf3[0xA8:0xD0]
print("  0xA8..0xD0 (%d 字节): %s" % (len(seg), seg.hex(" ")))
