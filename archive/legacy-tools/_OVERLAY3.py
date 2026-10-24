# -*- coding: utf-8 -*-
# 重建贴图遮盖 PEG（修正字形定位 + 完整 DXT3 mip 链 + PNG 预览）
import sys, os, struct, zlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp, dec_block, enc_block, px_at, BW

OUT = r"F:/sr2-cn/_OVERLAY3"
os.makedirs(OUT, exist_ok=True)
CN = r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/patch.vpp_pc"
f = Font(CN)
# 关键（模板匹配实测，12/12 字偏移恒为 -5）：
# 引擎用的汉化 vf3 = dd72f198（v10 patch 与 v10 common 完全相同）；
# 但 v10 patch 图集（340340761dda）的字形顺序比 charlist 少 5：
#   charlist[k] 的字形在图集 uv(k - 5) 处。
# 官方图集(a8c33f12…)与 textures 图集(62a57046…)偏移杂乱，均不可用。
ATLAS_VPP = r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/patch.vpp_pc"
if ATLAS_VPP:
    av = Vpp(ATLAS_VPP)
    ae = av.find("fnt_chinese", "g_peg_pc")
    if not ae:
        raise SystemExit("图集缺失: %s" % ATLAS_VPP)
    f.atlas = av.read(ae)
    print("图集来源: v10 patch  md5=%s" % __import__("hashlib").md5(f.atlas).hexdigest())
GLYPH_OFFSET = -5                            # charlist[k] 的字形在 uv(k-5)
CL = f.charlist
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
PAD, SZ = 3, 31                              # 字形格子 31x31，外留 3px pad
COLS = 65                                    # 图集 65 列网格（已验证）


def uv_grid(k):
    """v10 汉化图集真实排布：每行 65 格，但前 5 列在 x=1..125、后 60 列在 x=156..1985；
    k 的编号是「先填后 60 列(col5..64)，再填下一行前 5 列(col0..4)」。
    vf3 的 V 数组末尾缺 5 项，故 k>=2790 直接用此公式推算。"""
    b = k // COLS
    p = k % COLS
    if p < 60:
        x = 156 + 31 * p
        y = 1 + 31 * b
    else:
        x = 1 + 31 * (p - 60)
        y = 1 + 31 * (b + 1)
    return (x, y)


# 自检：uv_grid 必须与 f.uv 在可读范围内（k<2790）完全一致
_chk = 0
for _k in range(0, min(f.N, 2790)):
    if uv_grid(_k) != f.uv(_k):
        print("WARN uv_grid 不一致 k=%d grid=%s uv=%s" % (_k, uv_grid(_k), f.uv(_k)))
        _chk += 1
print("uv_grid 自检：%d 处不一致（应为 0）" % _chk)



def cell_alpha(ch):
    """返回 31x31 的 alpha（0-255），字形位置 = uv(charlist_idx + GLYPH_OFFSET)。"""
    k = f.idx(ch)
    if k is None:
        return [[0] * SZ for _ in range(SZ)]
    kk = k + GLYPH_OFFSET
    if kk < 0:
        kk = 0
    try:
        x, y = f.uv(kk)         # 实际 vf3 数据
    except Exception:
        x, y = uv_grid(kk)      # 末尾 5 项 V 数组被截断，用网格公式
    x -= PAD; y -= PAD
    out = []
    for yy in range(SZ):
        row = []
        for xx in range(SZ):
            X, Y = x + xx, y + yy
            if X < 0 or Y < 0 or X >= 2048 or Y >= 2048:
                row.append(0); continue
            row.append(px_at(f.atlas, X, Y)[3])
        out.append(row)
    return out


def mip_bytes(w, h):
    total = 0; cw, ch = w, h
    while True:
        bw = (cw + 3) // 4; bh = (ch + 3) // 4
        if bw <= 0 or bh <= 0: break
        total += bw * bh * 16
        nw, nh = max(1, cw // 2), max(1, ch // 2)
        if nw == cw and nh == ch: break
        cw, ch = nw, nh
    return total


def build(name, text):
    n = len(text)
    W = ((n * (SZ + 2) + 4) + 3) // 4 * 4     # 每字 33 宽槽位，4 对齐
    H = ((SZ + 8) + 3) // 4 * 4               # 高度 4 对齐
    # 源 RGBA：白字（rgb=alpha）透明底
    src = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    for i, ch in enumerate(text):
        if ch not in bidx:
            continue
        g = cell_alpha(ch)
        ox, oy = 2 + i * (SZ + 2), 4
        for yy in range(SZ):
            for xx in range(SZ):
                if 0 <= oy + yy < H and 0 <= ox + xx < W:
                    a = g[yy][xx]
                    src[oy + yy][ox + xx] = (a, a, a, a)

    # 编码完整 mip 链（DXT3）
    def avg4(cur, y0, x0, h, w):
        xs = [min(x0, w - 1), min(x0 + 1, w - 1)]
        ys = [min(y0, h - 1), min(y0 + 1, h - 1)]
        r = g = b = a = 0
        for yy in ys:
            for xx in xs:
                pr, pg, pb, pa = cur[yy][xx]
                r += pr; g += pg; b += pb; a += pa
        c = len(xs) * len(ys)
        return (r // c, g // c, b // c, a // c)

    out = bytearray()
    cur = src
    while True:
        h = len(cur); w = len(cur[0])
        bw = (w + 3) // 4; bh = (h + 3) // 4
        for by in range(bh):
            for bx in range(bw):
                block = [[cur[min(by * 4 + yy, h - 1)][min(bx * 4 + xx, w - 1)]
                          for xx in range(4)] for yy in range(4)]
                out += enc_block(block)
        nw, nh = max(1, w // 2), max(1, h // 2)
        if nw == w and nh == h: break
        cur = [[avg4(cur, y * 2, x * 2, h, w) for x in range(nw)] for y in range(nh)]

    expect = mip_bytes(W, H)
    assert len(out) == expect, "mip size %d != expected %d" % (len(out), expect)

    # GEKV peg_pc（结构照抄 ui_btnmash_nx）
    names = (name + ".tga").encode() + b"\x00"
    hdr = bytearray(0x48)
    hdr[0:4] = b"GEKV"
    struct.pack_into("<I", hdr, 4, 10)
    struct.pack_into("<I", hdr, 8, 0x48 + len(names))
    struct.pack_into("<I", hdr, 12, len(out))      # 0x0C = g_peg_pc 数据大小（关键！否则越界崩溃）
    struct.pack_into("<I", hdr, 16, 1)
    struct.pack_into("<I", hdr, 20, 0x00100001)
    struct.pack_into("<I", hdr, 24, 0)
    struct.pack_into("<HH", hdr, 28, W, H)
    struct.pack_into("<I", hdr, 32, 0x192)          # DXT3
    struct.pack_into("<I", hdr, 36, 0)
    struct.pack_into("<HH", hdr, 40, 1, 1)
    struct.pack_into("<I", hdr, 44, 0)
    struct.pack_into("<I", hdr, 48, 0x0a010000)
    struct.pack_into("<I", hdr, 52, len(out))      # 0x34 同 0x0C
    # 0x38..0x47 必须保持全 0（与 ui_btnmash_nx 等参考 peg 一致；此处不再写 0x44）
    open(os.path.join(OUT, name + ".peg_pc"), "wb").write(bytes(hdr) + names)
    open(os.path.join(OUT, name + ".g_peg_pc"), "wb").write(bytes(out))

    # xtbl（单条目，StartX/Y=1,1，整张图集即一行字幕）
    xt = ['<root>', '<Table>', '\t<BitmapSheets>', '\t\t<Name>%s</Name>' % name,
          '\t\t<Images>', '\t\t\t<Properties>', '\t\t\t\t<Name>%s</Name>' % name,
          '\t\t\t\t<StartX>1</StartX>', '\t\t\t\t<StartY>1</StartY>',
          '\t\t\t\t<ImageWidth>%d</ImageWidth>' % W,
          '\t\t\t\t<ImageHeight>%d</ImageHeight>' % H,
          '\t\t\t</Properties>', '\t\t</Images>',
          '\t<_Editor>', '\t\t<Category>Entries</Category>', '\t\t</_Editor>',
          '\t</BitmapSheets>', '</Table>', '</root>']
    open(os.path.join(OUT, name + ".xtbl"), "w", encoding="utf-8").write("\n".join(xt))

    # PNG 预览（level0 源 RGBA）
    png_write(os.path.join(OUT, name + ".png"), src, W, H)
    print("%-10s 字幕=%s" % (name, text))
    print("           图集 %dx%d  g_peg_pc(mip链)=%d B  已写 PEG/xtbl/PNG" % (W, H, len(out)))


def png_write(path, rgba, w, h):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            r, g, b, a = rgba[y][x]
            raw += bytes((r, g, b, a))
    comp = zlib.compress(bytes(raw), 9)
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
    out += chunk(b"IDAT", comp)
    out += chunk(b"IEND", b"")
    open(path, "wb").write(out)


build("ui_sub1", "你的弟兄们需要你的保护")
build("ui_sub2", "你的弟兄们要出去谈几笔生意，保护他们免遭袭击")
print("\n输出目录:", OUT)
