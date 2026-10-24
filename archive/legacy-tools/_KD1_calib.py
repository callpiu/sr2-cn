# -*- coding: utf-8 -*-
# 校准：dump 原版 textures 图集在 common-vf3 的 (U,V) 附近的真实画面
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
            r.append(dict(idx=i, n=self.z(self.na, a), x=self.z(self.ea, b_) if b_ else "", o=dd, z=ln))
        return r

    def rd(self, e):
        p = self.ds + e["o"]
        return self.d[p:p + e["z"]]

    def find(self, n, x=None):
        for e in self.ents():
            if e["n"].lower() == n.lower() and (x is None or e["x"].lower() == x.lower()):
                return e
        return None


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


def region(d, x0, y0, w, h, scale, path):
    rows = [[dec_px(d, x0 + xx, y0 + yy) for xx in range(w)] for yy in range(h)]
    png_gray(rows, scale, path)
    print("saved %s  (%d,%d)-(%d,%d) scale=%d" % (path, x0, y0, x0 + w, y0 + h, scale))


vt = Vpp(os.path.join(G, "textures.vpp_pc"))
T = vt.rd(vt.find("fnt_chinese"))
vc = Vpp(os.path.join(G, "common.vpp_pc"))
VFc = vc.rd(vc.find("fnt_chinese", "vf3_pc"))


def uvv(vf, k):
    N = struct.unpack_from("<I", vf, 8)[0]
    U = 0xD0 + N * 16
    V = U + N * 4
    return (struct.unpack_from("<i", vf, U + k * 4)[0],
            struct.unpack_from("<i", vf, V + k * 4)[0])


# 1) ASCII 区：idx 33 期望 'A'，U=686
u, v = uvv(VFc, 33)
print("common-vf3 idx33 (A) U=%d V=%d" % (u, v))
region(T, u - 60, 0, 260, 30, 4, r"F:/sr2-cn/_KD_ascii.png")

# 2) CJK 区：idx 333 期望 '你'，U=301 V=125
u, v = uvv(VFc, 333)
print("common-vf3 idx333 (你) U=%d V=%d" % (u, v))
region(T, u - 40, v - 20, 240, 90, 4, r"F:/sr2-cn/_KD_cjk.png")

# 3) 顺便 dump 整个 ASCII 行（前 1024 px）看序列
region(T, 0, 0, 1024, 28, 2, r"F:/sr2-cn/_KD_row0.png")
