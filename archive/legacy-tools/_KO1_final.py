# -*- coding: utf-8 -*-
# 验证部署后的补丁：裁 23 个目标格子
import os, re, struct, zlib

FIX = r"F:/sr2-cn/_FIX/patch.vpp_pc"
ORIG = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
BW = 2048 // 4


class Vpp:
    def __init__(self, path):
        self.f = open(path, "rb")
        head = self.f.read(0x400000)
        o = 5 + 0x14F
        self.num = struct.unpack_from("<i", head, o)[0]
        self.lo = struct.unpack_from("<i", head, o + 8)[0]
        self.lf = struct.unpack_from("<i", head, o + 12)[0]
        self.le = struct.unpack_from("<i", head, o + 16)[0]
        self.na = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ea = ((self.na + self.lf) & 0xFFFFF800) + 0x800
        self.ds = ((self.ea + self.le) & 0xFFFFF800) + 0x800
        self.meta = head

    def z(self, p):
        e = self.meta.find(b"\x00", p)
        return self.meta[p:e].decode("ascii", "replace")

    def ents(self):
        r = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b_, c, dd, ln = struct.unpack_from("<IIiii", self.meta, e)
            r.append(dict(idx=i, n=self.z(self.na + a), x=self.z(self.ea + b_) if b_ else "", o=dd, z=ln))
        return r

    def find(self, n, x=None):
        for e in self.ents():
            if e["n"].lower() == n.lower() and (x is None or e["x"].lower() == x.lower()):
                return e
        return None

    def read_at(self, off, size):
        self.f.seek(off)
        return self.f.read(size)


def rgb565(v):
    return (((v >> 11) & 0x1F) * 255 // 31, ((v >> 5) & 0x3F) * 255 // 63, (v & 0x1F) * 255 // 31)


def dec_px(d, X, Y):
    if X < 0 or Y < 0 or X >= 2048 or Y >= 2048:
        return 0
    o = ((Y // 4) * BW + X // 4) * 16
    b = d[o:o + 16]
    c0 = b[8] | (b[9] << 8)
    c1 = b[10] | (b[11] << 8)
    idx = int.from_bytes(bytes(b[12:16]), "little")
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


def sheet(cells, scale=3, cols=12, gap=3, path="s.png"):
    cw = 34 * scale
    rowsn = (len(cells) + cols - 1) // cols
    cv = [[25] * (cols * (cw + gap)) for _ in range(rowsn * (cw + gap))]
    for n, c in enumerate(cells):
        px = (n % cols) * (cw + gap)
        py = (n // cols) * (cw + gap)
        for yy in range(cw):
            for xx in range(cw):
                cv[py + yy][px + xx] = c[yy // scale][xx // scale]
    png_gray(cv, 1, path)


v = Vpp(FIX)
at = v.read_at(v.ds + v.find("fnt_chinese", "g_peg_pc")["o"], 4194304)
ve = v.find("fnt_chinese", "vf3_pc")
vf = v.read_at(v.ds + ve["o"], ve["z"])
N = struct.unpack_from("<I", vf, 8)[0]
UOFF = 0xD0 + N * 16
VOFF = UOFF + N * 4


def uv(k):
    return (struct.unpack_from("<i", vf, UOFF + k * 4)[0],
            struct.unpack_from("<i", vf, VOFF + k * 4)[0])


ce = v.find("charlist_CH", "txt")
cl = v.read_at(v.ds + ce["o"], ce["z"])
m = re.search(rb"count\s*=\s*(\d+)", cl)
body = cl[m.end():] if m else cl
end = body.find(b"//ENDOFFILE")
OFF = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]

PAIRS = [("交", 287), ("他", 301), ("你", 336), ("保", 354), ("們", 362),
         ("兄", 410), ("免", 417), ("到", 458), ("去", 535), ("受", 543),
         ("弟", 967), ("擊", 1221), ("攻", 1243), ("易", 1292), ("正", 1458),
         ("的", 1784), ("要", 2268), ("護", 2342), ("行", 2234), ("進", 2491),
         ("避", 2514), ("需", 2656), ("，", 2809)]

cells = []
for c, J in PAIRS:
    u, vv = uv(J - 5)
    cells.append([[dec_px(at, u - 2 + xx, vv - 2 + yy) for xx in range(34)] for yy in range(34)])
sheet(cells, path=r"F:/sr2-cn/_KO_final.png")
print("_KO_final.png 顺序（应读出这 23 个正确字）：")
print("  " + " ".join(c for c, _ in PAIRS))
