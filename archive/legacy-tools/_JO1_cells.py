# -*- coding: utf-8 -*-
# 从 patch.vpp_pc 的 fnt_chinese.g_peg_pc 里裁出关键字形格子，验证「图集顺序 == 哪张表」
import os, struct, zlib, re

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"


class Vpp:
    def __init__(self, path):
        self.d = open(path, "rb").read()
        o = 5 + 0x14F
        self.num = struct.unpack_from("<i", self.d, o)[0]
        self.lo = struct.unpack_from("<i", self.d, o + 8)[0]
        self.lf = struct.unpack_from("<i", self.d, o + 12)[0]
        self.le = struct.unpack_from("<i", self.d, o + 16)[0]
        self.na = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ea = ((self.na + self.lf) & 0xFFFFF800) + 0x800
        self.ds = ((self.ea + self.le) & 0xFFFFF800) + 0x800

    def z(self, b, p):
        e = self.d.find(b"\x00", b + p)
        return self.d[b + p:e].decode("ascii", "replace")

    def ents(self):
        r = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b_, c, dd, ln = struct.unpack_from("<IIiii", self.d, e)
            r.append(dict(n=self.z(self.na, a), x=self.z(self.ea, b_) if b_ else "", o=dd, z=ln))
        return r

    def rd(self, e):
        p = self.ds + e["o"]
        return self.d[p:p + e["z"]]

    def find(self, n, x=None):
        for e in self.ents():
            if e["n"].lower() == n.lower() and (x is None or e["x"].lower() == x.lower()):
                return e
        return None


def load_cl(v, fname):
    b = v.rd(v.find(fname, "txt"))
    m = re.search(rb"count\s*=\s*(\d+)", b)
    body = b[m.end():] if m else b
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


W = H = 2048
BW = W // 4  # 512 blocks per row


def rgb565(v):
    r = ((v >> 11) & 0x1F) * 255 // 31
    g = ((v >> 5) & 0x3F) * 255 // 63
    b = (v & 0x1F) * 255 // 31
    return r, g, b


def decode_block(d, bx, by):
    o = (by * BW + bx) * 16
    blk = d[o:o + 16]
    if len(blk) < 16:
        return None
    c0 = blk[8] | (blk[9] << 8)
    c1 = blk[10] | (blk[11] << 8)
    idx = int.from_bytes(blk[12:16], "little")
    r0, g0, b0 = rgb565(c0)
    r1, g1, b1 = rgb565(c1)
    if c0 > c1:
        pal = [(r0, g0, b0), (r1, g1, b1),
               ((2 * r0 + r1) // 3, (2 * g0 + g1) // 3, (2 * b0 + b1) // 3),
               ((r0 + 2 * r1) // 3, (g0 + 2 * g1) // 3, (b0 + 2 * b1) // 3)]
    else:
        pal = [(r0, g0, b0), (r1, g1, b1),
               ((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2), (0, 0, 0)]
    px = []
    for py in range(4):
        row = []
        for pxx in range(4):
            k = py * 4 + pxx
            a4 = (blk[k // 2] >> (4 * (k % 2))) & 0xF
            r, g, b = pal[(idx >> (2 * k)) & 3]
            a = a4 * 17
            # 合成到白底：字形是暗色墨迹
            lum = (r * 299 + g * 587 + b * 114) // 1000
            row.append((lum, a))
        px.append(row)
    return px


def cell_xy(index, cols=66, pitch=31, x0=2, y0=34, ascii_count=94):
    k = index - ascii_count
    col = k % cols
    row = k // cols
    return x0 + pitch * col, y0 + pitch * row


def crop(d, x, y, w=31, h=31):
    """返回 w*h 的灰度图（白底黑字）。"""
    out = [[255] * w for _ in range(h)]
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            blk = decode_block(d, xx // 4, yy // 4)
            if blk is None:
                continue
            lum, a = blk[yy % 4][xx % 4]
            v = 255 - ((255 - lum) * a) // 255
            out[yy - y][xx - x] = max(0, min(255, v))
    return out


def png_gray(rows, scale=4, path="out.png"):
    h = len(rows) * scale
    w = len(rows[0]) * scale
    raw = bytearray()
    for r in rows:
        line = bytearray()
        for v in r:
            line += bytes([v]) * scale
        for _ in range(scale):
            raw += b"\x00" + bytes(line)

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    out += chunk(b"IEND", b"")
    open(path, "wb").write(out)


def png_sheet(cells, labels, scale=4, cols=6, path="sheet.png"):
    cw = 31 * scale
    gap = 6
    lab = 12
    rowsn = (len(cells) + cols - 1) // cols
    Wt = cols * (cw + gap)
    Ht = rowsn * (cw + lab + gap)
    canvas = [[40] * Wt for _ in range(Ht)]
    for n, cellimg in enumerate(cells):
        px = (n % cols) * (cw + gap)
        py = (n // cols) * (cw + lab + gap) + lab
        for yy in range(cw):
            for xx in range(cw):
                canvas[py + yy][px + xx] = cellimg[yy // scale][xx // scale]
    png_gray(canvas, 1, path)
    print("saved", path, labels)


v = Vpp(os.path.join(G, "patch.vpp_pc"))
OFF = load_cl(v, "charlist_CH")
B = load_cl(Vpp(r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2"), "charlist_CH")
d = v.rd(v.find("fnt_chinese", "g_peg_pc"))
print("atlas bytes =", len(d))

TESTS = [
    (371, "B[371]=%s" % chr(B[371])),
    (333, "OFF[333]=%s" % chr(OFF[333])),
    (336, "OFF[336]=%s / B[336]=%s" % (chr(OFF[336]), chr(B[336]))),
    (1836, "B[1836]=%s" % chr(B[1836])),
    (1787, "OFF[1787]=%s" % chr(OFF[1787])),
    (1784, "OFF[1784]=%s / B[1784]=%s" % (chr(OFF[1784]), chr(B[1784]))),
]
cells = []
labels = []
for idx, tag in TESTS:
    x, y = cell_xy(idx)
    print("idx %-5d cell=(%d,%d)  %s" % (idx, x, y, tag))
    cells.append(crop(d, x, y))
    labels.append(tag)
png_sheet(cells, labels, scale=4, cols=6, path=r"F:/sr2-cn/_CHK_atlas_order.png")
