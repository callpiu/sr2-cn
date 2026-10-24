# -*- coding: utf-8 -*-
# 用 65 列/31 步距网格裁 idx 330..345，验证 patch 与 textures 图集各自的「顺序」
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


def load_cl(v, fname="charlist_CH"):
    b = v.rd(v.find(fname, "txt"))
    m = re.search(rb"count\s*=\s*(\d+)", b)
    body = b[m.end():] if m else b
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


BW = 2048 // 4


def rgb565(v):
    return (((v >> 11) & 0x1F) * 255 // 31, ((v >> 5) & 0x3F) * 255 // 63, (v & 0x1F) * 255 // 31)


def dec_px(d, X, Y):
    if X < 0 or Y < 0 or X >= 2048 or Y >= 2048:
        return 0
    o = ((Y // 4) * BW + X // 4) * 16
    b = d[o:o + 16]
    c0 = b[8] | (b[9] << 8)
    c1 = b[10] | (b[11] << 8)
    idx = int.from_bytes(b[12:16], "little")
    p0 = rgb565(c0)
    p1 = rgb565(c1)
    if c0 > c1:
        pal = [p0, p1, tuple((2 * p0[i] + p1[i]) // 3 for i in range(3)),
               tuple((p0[i] + 2 * p1[i]) // 3 for i in range(3))]
    else:
        pal = [p0, p1, tuple((p0[i] + p1[i]) // 2 for i in range(3)), (0, 0, 0)]
    k = (Y % 4) * 4 + (X % 4)
    r, g, bl = pal[(idx >> (2 * k)) & 3]
    return (r * 299 + g * 587 + bl * 114) // 1000


def crop(d, x, y, w=32, h=32):
    return [[dec_px(d, x + xx, y + yy) for xx in range(w)] for yy in range(h)]


def png_gray(rows, scale, path):
    h, w = len(rows) * scale, len(rows[0]) * scale
    raw = bytearray()
    for r in rows:
        line = bytearray()
        for v in r:
            line += bytes([v]) * scale
        for _ in range(scale):
            raw += b"\x00" + bytes(line)

    def ck(t, dd):
        c = t + dd
        return struct.pack(">I", len(dd)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    o = b"\x89PNG\r\n\x1a\n" + ck(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
    o += ck(b"IDAT", zlib.compress(bytes(raw), 6)) + ck(b"IEND", b"")
    open(path, "wb").write(o)


def sheet(cells, scale=4, cols=16, gap=4, path="s.png"):
    cw = 32 * scale
    rowsn = (len(cells) + cols - 1) // cols
    Wt = cols * (cw + gap)
    Ht = rowsn * (cw + gap)
    cv = [[20] * Wt for _ in range(Ht)]
    for n, c in enumerate(cells):
        px = (n % cols) * (cw + gap)
        py = (n // cols) * (cw + gap)
        for yy in range(cw):
            for xx in range(cw):
                cv[py + yy][px + xx] = c[yy // scale][xx // scale]
    png_gray(cv, 1, path)


vp = Vpp(os.path.join(G, "patch.vpp_pc"))
A = vp.rd(vp.find("fnt_chinese", "g_peg_pc"))
OFF = load_cl(vp)
B = load_cl(Vpp(r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
T = vt.rd(vt.find("fnt_chinese"))

IDXS = list(range(326, 342)) + list(range(366, 382))
print("OFF:", " ".join(chr(OFF[i]) for i in IDXS))
print("B  :", " ".join(chr(B[i]) if i < len(B) else "?" for i in IDXS))

for tag, d in (("patch", A), ("textures", T)):
    cells = []
    for k in IDXS:
        cx, cy = 1 + 31 * (k % 65), 1 + 31 * (k // 65)
        cells.append(crop(d, cx, cy))
    sheet(cells, path=r"F:/sr2-cn/_JU_%s_grid65.png" % tag)
    print("saved _JU_%s_grid65.png" % tag)
