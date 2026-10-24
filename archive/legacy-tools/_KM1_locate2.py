# -*- coding: utf-8 -*-
# 定位「行」和「，」的引擎格子并视觉验证
import os, re, struct, zlib

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
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


def sheet(cells, scale=3, cols=8, gap=4, path="s.png"):
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


vo = Vpp(ORIG)
atlas = vo.read_at(vo.ds + vo.find("fnt_chinese", "g_peg_pc")["o"], 4194304)
vfe = vo.find("fnt_chinese", "vf3_pc")
vf = vo.read_at(vo.ds + vfe["o"], vfe["z"])
N = struct.unpack_from("<I", vf, 8)[0]
UOFF = 0xD0 + N * 16
VOFF = UOFF + N * 4


def uv(k):
    return (struct.unpack_from("<i", vf, UOFF + k * 4)[0],
            struct.unpack_from("<i", vf, VOFF + k * 4)[0])


cle = vo.find("charlist_CH", "txt")
cl = vo.read_at(vo.ds + cle["o"], cle["z"])
m = re.search(rb"count\s*=\s*(\d+)", cl)
body = cl[m.end():] if m else cl
end = body.find(b"//ENDOFFILE")
OFF = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]

for ch in "行螢，點":
    cp = ord(ch)
    print("  %s U+%04X -> %s" % (ch, cp, OFF.index(cp) if cp in OFF else "不在 charlist"))

iHang = OFF.index(ord("行"))
iYing = OFF.index(ord("螢"))
iCom = OFF.index(ord("，")) if ord("，") in OFF else None
iDian = OFF.index(ord("點")) if ord("點") in OFF else None

print("\n行: 源格子 = %d, 目标格子 = %d" % (iHang - 5, iYing - 5))
if iCom and iDian:
    print("，: 源格子 = %d, 目标格子 = %d" % (iCom - 5, iDian - 5))

cells = []
labels = []
for tag, src, dst in [("行", iHang, iYing)] + ([("，", iCom, iDian)] if iCom and iDian else []):
    u, v = uv(src - 5)
    cells.append([[dec_px(atlas, u - 2 + xx, v - 2 + yy) for xx in range(34)] for yy in range(34)])
    labels.append("%s源%d" % (tag, src - 5))
    u, v = uv(dst - 5)
    cells.append([[dec_px(atlas, u - 2 + xx, v - 2 + yy) for xx in range(34)] for yy in range(34)])
    labels.append("%s目标%d" % (tag, dst - 5))
sheet(cells, path=r"F:/sr2-cn/_KM_check.png")
print("\n顺序:", labels)
print("_KM_check.png：每对 = [源格子(应为正确字), 目标格子(应为当前错误显示的字)]")
