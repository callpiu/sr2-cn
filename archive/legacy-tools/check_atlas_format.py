# -*- coding: utf-8 -*-
"""检查 fnt_body_n / fnt_body_s / fnt_chinese 图集的真实格式与尺寸。

从描述符字段推测：
    +0x08 (u32)  描述符长度 (0x5D=93 / 0x5E=94)
    +0x0C (u32)  fnt_body_s 特有值 0x55500
    +0x0E (byte) 0x04 / 0x05 / 0x40
    +0x1D (byte) 0x02 / 0x08
    +0x1F (byte) 0x02 / 0x08
    +0x20 (u16)  0x0191 / 0x0192
    +0x33 (byte) 0x01 / 0x08
    +0x34 (byte) 0x00 / 0x50
    +0x35 (byte) 0x00 / 0x55
    +0x36 (byte) 0x04 / 0x05 / 0x40   (与 +0x0E 同)
"""
import os, struct, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
NAMES = ["fnt_body_n", "fnt_body_s", "fnt_chinese"]

# 图集大小与描述符关键字段
descs = {}
with LightVpp(os.path.join(G, "pegs.vpp_pc")) as pv:
    for e in pv.entries():
        nm = pv.name(e)
        if nm in NAMES:
            descs[nm] = pv.read(e)

texs = {}
with LightVpp(os.path.join(G, "textures.vpp_pc")) as tv:
    for e in tv.entries():
        nm = tv.name(e)
        if nm in NAMES:
            texs[nm] = (e["size"], e["body"])

print("%-14s %-10s %-6s %-6s %-6s %-6s %-8s %-8s" %
      ("name", "atlas", "b0E", "b1D", "b1F", "b20", "b33", "b34-35"))
for nm in NAMES:
    d = descs[nm]
    sz = texs[nm][0]
    print("%-14s %-10d 0x%02X   0x%02X   0x%02X   0x%04X  0x%02X   0x%02X%02X" %
          (nm, sz, d[0x0E], d[0x1D], d[0x1F],
           struct.unpack_from("<H", d, 0x20)[0], d[0x33], d[0x34], d[0x35]))
print()

# 从 atlas 大小反推尺寸（DXT3 = 1 byte/px）
print("=== 图集尺寸反推（DXT3 = 1 字节/像素）===")
for nm in NAMES:
    sz = texs[nm][0]
    # 可能是 2 的幂组合
    cands = []
    for w in (64, 128, 256, 512, 1024, 2048, 4096):
        if sz % w == 0:
            h = sz // w
            if h in (64, 128, 256, 512, 1024, 2048, 4096):
                cands.append((w, h))
    print("  %-14s %9d  ->  %s" % (nm, sz, cands))
print()

# 读图集头 64 字节，看有无 TGA 头特征
print("=== 图集前 64 字节 ===")
with LightVpp(os.path.join(G, "textures.vpp_pc")) as tv:
    for e in tv.entries():
        nm = tv.name(e)
        if nm in NAMES:
            d = tv.read(e)
            print("  %s (%d 字节):" % (nm, len(d)))
            print("     %s" % d[:64].hex(" "))
            # TGA 头：@2 = 图像类型(2=未压缩真彩,10=RLE真彩)
            print("     TGA 可能: idlen=%d cmaptype=%d imgtype=%d  w=%d h=%d bpp=%d" %
                  (d[0], d[1], d[2],
                   struct.unpack_from("<H", d, 12)[0], struct.unpack_from("<H", d, 14)[0], d[16]))
            print()
