# -*- coding: utf-8 -*-
# 贴图遮盖 第2步：把两张字幕图打包成 PEG（GEKV 描述符 + DXT3 图集）
# 纯 Python：自己解析 PNG 灰度 + DXT3 编码 + 写 GEKV
import sys, os, struct, zlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import dec_block, enc_block, png_gray

OUTDIR = r"F:/sr2-cn/_OVERLAY"
os.makedirs(OUTDIR, exist_ok=True)


def load_png_gray(path):
    d = open(path, "rb").read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n"
    o = 8
    idat = b""
    w = h = 0
    while o < len(d):
        ln, typ = struct.unpack_from(">I4s", d, o)
        body = d[o + 8:o + 8 + ln]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack_from(">IIBB", body, 0)
            assert bd == 8 and ct == 0, (bd, ct)
        elif typ == b"IDAT":
            idat += body
        o += 12 + ln
    raw = zlib.decompress(idat)
    stride = w + 1
    rows = []
    prev = bytearray(w)
    for y in range(h):
        f = raw[y * stride]
        line = bytearray(raw[y * stride + 1:(y + 1) * stride])
        if f == 1:
            for i in range(w):
                line[i] = (line[i] + line[i - 1]) & 0xFF if i else line[i]
        elif f == 2:
            for i in range(w):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(w):
                a = line[i - 1] if i else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(w):
                a = line[i - 1] if i else 0
                b = prev[i]
                c = prev[i - 1] if i else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        rows.append(list(line))
        prev = line
    return rows, w, h


AW, AH, ROWH = 1024, 128, 64
g1, w1, h1 = load_png_gray(r"F:/sr2-cn/_ovl_sub1.png")
g2, w2, h2 = load_png_gray(r"F:/sr2-cn/_ovl_sub2.png")
print("图1 %dx%d  图2 %dx%d" % (w1, h1, w2, h2))

# 组装 1024x128 灰度图集（alpha 通道用灰度值）
atlas = [[0] * AW for _ in range(AH)]
for y in range(h1):
    for x in range(w1):
        atlas[y][x] = g1[y][x]
oy = ROWH
for y in range(h2):
    for x in range(w2):
        if oy + y < AH:
            atlas[oy + y][x] = g2[y][x]

# DXT3 编码（复刻本图集的「预乘灰度」方式：alpha=灰度，rgb=灰）
BW = AW // 4
BH = AH // 4
out = bytearray()
for by in range(BH):
    for bx in range(BW):
        px = []
        for yy in range(4):
            row = []
            for xx in range(4):
                a = atlas[by * 4 + yy][bx * 4 + xx]
                row.append((a, a, a, a))
            px.append(row)
        out += enc_block(px)
print("图集 DXT3 = %d B（%dx%d）" % (len(out), AW, AH))

# --- 写 GEKV 描述符（照抄 ui_btnmash_nx.peg_pc 的头部结构，2 条目）---
def build_gekv(entries, total_entries):
    """entries = [(name, w, h)]；头部结构照抄现有 peg"""
    names = b"".join(n.encode() + b"\x00" for n, _, _ in entries)
    hdr = bytearray(0x48)
    hdr[0:4] = b"GEKV"
    struct.pack_into("<I", hdr, 4, 10)            # version
    struct.pack_into("<I", hdr, 8, 0)             # total size，稍后回填
    struct.pack_into("<I", hdr, 12, 0x00050050)
    struct.pack_into("<I", hdr, 16, total_entries)
    struct.pack_into("<I", hdr, 20, 0x00100001)
    struct.pack_into("<I", hdr, 24, 0)
    struct.pack_into("<H", hdr, 28, AW)           # 图集宽
    struct.pack_into("<H", hdr, 30, AH)           # 图集高
    struct.pack_into("<I", hdr, 32, 0x192)
    struct.pack_into("<I", hdr, 36, 0)
    struct.pack_into("<HH", hdr, 40, 1, 1)
    struct.pack_into("<I", hdr, 44, 0)
    struct.pack_into("<I", hdr, 48, 0x0a010000)
    struct.pack_into("<I", hdr, 52, 0x00050050)
    struct.pack_into("<I", hdr, 68, 0x48 + len(names))
    struct.pack_into("<I", hdr, 8, 0x48 + len(names))
    return bytes(hdr) + names


entries = [
    ("ui_sub_fix_1.tga", w1, h1),
    ("ui_sub_fix_2.tga", w2, h2),
]
gekv = build_gekv(entries, 2)
open(os.path.join(OUTDIR, "ui_sub_fix.peg_pc"), "wb").write(gekv)
open(os.path.join(OUTDIR, "ui_sub_fix.g_peg_pc"), "wb").write(bytes(out))
print("已写 ui_sub_fix.peg_pc (%d B) 与 ui_sub_fix.g_peg_pc (%d B)" % (len(gekv), len(out)))

# --- 写 xtbl（BitmapSheets）---
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


xt = ['<root>', '<Table>']
for i, (n, w, h) in enumerate(entries):
    y = 0 if i == 0 else ROWH
    xt += [
        '\t<BitmapSheets>',
        '\t\t<Name>ui_sub_fix</Name>',
        '\t\t<Images>',
        '\t\t\t<Properties>',
        '\t\t\t\t<Name>%s</Name>' % esc(n[:-4]),
        '\t\t\t\t<StartX>1</StartX>',
        '\t\t\t\t<StartY>%d</StartY>' % (y + 1),
        '\t\t\t\t<ImageWidth>%d</ImageWidth>' % w,
        '\t\t\t\t<ImageHeight>%d</ImageHeight>' % h,
        '\t\t\t</Properties>',
        '\t\t</Images>',
        '\t<_Editor>',
        '\t\t<Category>Entries</Category>',
        '\t\t</_Editor>',
        '\t</BitmapSheets>',
    ]
xt += ['</Table>', '</root>']
open(os.path.join(OUTDIR, "ui_sub_fix.xtbl"), "w", encoding="utf-8").write("\n".join(xt))
print("已写 ui_sub_fix.xtbl")
print("\n条目:")
for i, (n, w, h) in enumerate(entries):
    print("  %s  %dx%d  at (1,%d)" % (n, w, h, (0 if i == 0 else ROWH) + 1))
