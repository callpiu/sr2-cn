# -*- coding: utf-8 -*-
# 重建贴图遮盖：两个独立单条目 PEG（照抄 ui_btnmash_nx 结构）
import sys, os, struct, zlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, dec_block, enc_block, png_gray

OUT = r"F:/sr2-cn/_OVERLAY2"
os.makedirs(OUT, exist_ok=True)
CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
OFF, CELL, PAD, SZ = 5, 31, 3, 37


def load_png_gray(path):
    d = open(path, "rb").read()
    o, idat, w, h = 8, b"", 0, 0
    while o < len(d):
        ln, typ = struct.unpack_from(">I4s", d, o)
        body = d[o + 8:o + 8 + ln]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack_from(">IIBB", body, 0)
        elif typ == b"IDAT":
            idat += body
        o += 12 + ln
    raw = zlib.decompress(idat)
    rows, prev = [], bytearray(w)
    for y in range(h):
        fl = raw[y * (w + 1)]
        line = bytearray(raw[y * (w + 1) + 1:(y + 1) * (w + 1)])
        if fl == 1:
            for i in range(w):
                line[i] = (line[i] + (line[i - 1] if i else 0)) & 0xFF
        elif fl == 2:
            for i in range(w):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif fl == 3:
            for i in range(w):
                a = line[i - 1] if i else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        rows.append(list(line)); prev = line
    return rows, w, h


def cell_gray(k):
    x, y = f.uv(k)
    x -= PAD; y -= PAD
    return [[dec_block(f.atlas, (((y + yy) // 4) * 512 + ((x + xx) // 4)) * 16)[(y + yy) % 4][(x + xx) % 4][3]
             for xx in range(SZ)] for yy in range(SZ)]


def build(name, text):
    """图集尺寸 = 条目尺寸（4 对齐），单条目"""
    W = ((len(text) * (SZ + 2) + 4) + 3) // 4 * 4
    H = ((SZ + 8) + 3) // 4 * 4
    atlas = [[0] * W for _ in range(H)]
    for i, ch in enumerate(text):
        if ch not in bidx:
            continue
        g = cell_gray(bidx[ch] - OFF)
        ox, oy = 2 + i * (SZ + 2), 4
        for yy in range(SZ):
            for xx in range(SZ):
                if oy + yy < H and ox + xx < W:
                    atlas[oy + yy][ox + xx] = g[yy][xx]
    # DXT3
    out = bytearray()
    for by in range(H // 4):
        for bx in range(W // 4):
            px = [[(atlas[by*4+yy][bx*4+xx],)*3 + (atlas[by*4+yy][bx*4+xx],)
                   for xx in range(4)] for yy in range(4)]
            out += enc_block(px)
    # GEKV（结构照抄 ui_btnmash_nx）
    names = (name + ".tga").encode() + b"\x00"
    hdr = bytearray(0x48)
    hdr[0:4] = b"GEKV"
    struct.pack_into("<I", hdr, 4, 10)
    struct.pack_into("<I", hdr, 8, 0x48 + len(names))
    struct.pack_into("<I", hdr, 12, 0x00050050)
    struct.pack_into("<I", hdr, 16, 1)                 # 1 个条目
    struct.pack_into("<I", hdr, 20, 0x00100001)
    struct.pack_into("<I", hdr, 24, 0)
    struct.pack_into("<HH", hdr, 28, W, H)             # 条目宽高 = 图集宽高
    struct.pack_into("<I", hdr, 32, 0x192)
    struct.pack_into("<I", hdr, 36, 0)
    struct.pack_into("<HH", hdr, 40, 1, 1)
    struct.pack_into("<I", hdr, 44, 0)
    struct.pack_into("<I", hdr, 48, 0x0a010000)
    struct.pack_into("<I", hdr, 52, 0x00050050)
    struct.pack_into("<I", hdr, 68, 0x48 + len(names))
    open(os.path.join(OUT, name + ".peg_pc"), "wb").write(bytes(hdr) + names)
    open(os.path.join(OUT, name + ".g_peg_pc"), "wb").write(bytes(out))
    # xtbl（单条目，StartX/Y = 1,1）
    xt = ['<root>', '<Table>', '\t<BitmapSheets>', '\t\t<Name>%s</Name>' % name,
          '\t\t<Images>', '\t\t\t<Properties>', '\t\t\t\t<Name>%s</Name>' % name,
          '\t\t\t\t<StartX>1</StartX>', '\t\t\t\t<StartY>1</StartY>',
          '\t\t\t\t<ImageWidth>%d</ImageWidth>' % W,
          '\t\t\t\t<ImageHeight>%d</ImageHeight>' % H,
          '\t\t\t</Properties>', '\t\t</Images>',
          '\t<_Editor>', '\t\t<Category>Entries</Category>', '\t\t</_Editor>',
          '\t</BitmapSheets>', '</Table>', '</root>']
    open(os.path.join(OUT, name + ".xtbl"), "w", encoding="utf-8").write("\n".join(xt))
    print("%-10s 图集 %dx%d  DXT3 %d B  peg %d B" % (name, W, H, len(out), 0x48 + len(names)))


build("ui_sub1", "你的弟兄们需要你的保护")
build("ui_sub2", "你的弟兄们要出去谈几笔生意，保护他们免遭袭击")
print("\n输出目录:", OUT)
