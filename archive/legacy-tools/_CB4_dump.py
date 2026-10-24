# -*- coding: utf-8 -*-
"""dump vf3 两张表 + 裁剪图集行"""
import struct
from PIL import Image

d = open(r'F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc', 'rb').read()
N = 2795
A = 0xBC
A_SIZE = N * 16          # {a, b, 0, 0xFFFF}
B = A + A_SIZE
B_SIZE = N * 8
print("Table A: 0x%X..0x%X (%d rec x 16)" % (A, A + A_SIZE, N))
print("Table B: 0x%X..0x%X (%d rec x 8)" % (B, B + B_SIZE, N))
print("file end: 0x%X (len %d)" % (len(d), len(d)))

print("\n--- Table A 前 20 条 (a, b) ---")
for i in range(20):
    a, b, z, f = struct.unpack_from('<4I', d, A + i * 16)
    print("   #%-5d a=%-6d b=%-6d z=%d f=%d" % (i, a, b, z, f))

print("\n--- Table A 指定下标 ---")
for i in (403, 1868, 1067, 454, 364, 2699, 2328, 423, 1222, 1887, 582, 1447, 1977, 511, 0, 1, 224, 225):
    a, b, z, f = struct.unpack_from('<4I', d, A + i * 16)
    print("   #%-5d a=%-6d b=%-6d" % (i, a, b))

print("\n--- Table B 前 20 条 (2 u32) ---")
for i in range(20):
    p, q = struct.unpack_from('<2I', d, B + i * 8)
    print("   #%-5d p=%-8d q=%-8d  (hex %08X %08X)" % (i, p, q, p, q))

print("\n--- Table B 指定下标 ---")
for i in (403, 1868, 1067, 454, 364, 2699, 2328, 423, 1222, 1887, 582, 1447, 1977, 511, 0, 1, 224, 225):
    p, q = struct.unpack_from('<2I', d, B + i * 8)
    print("   #%-5d p=%-8d q=%-8d" % (i, p, q))

# ---------- 图集行裁剪 ----------
im = Image.open(r'F:\sr2-cn\_fontdump\atlas_full.png')
def strip(name, y0, h, x0=0, w=512, scale=4):
    c = im.crop((x0, y0, x0 + w, y0 + h)).resize((w * scale, h * scale), Image.NEAREST)
    c.save(r'F:\sr2-cn\_fontdump\%s.png' % name)
    print("saved", name, (x0, y0, w, h))

strip('row_384', 180, 70, 0, 512)     # 若 cell=32x30 从 y=8 起, row6 -> y=188
strip('row_1856', 920, 70, 0, 512)
