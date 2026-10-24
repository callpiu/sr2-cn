# -*- coding: utf-8 -*-
# 验证：源格子 = charlist.index(c) - 5，目标格子 = J(c) - 5
# 若成立，则「把源格子搬到目标格子」就能修好
import os, struct, zlib, re

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
OFFSET = 5


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


def crop(d, x, y, w=34, h=34):
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


def sheet(cells, scale=3, cols=11, gap=3, path="s.png"):
    cw = 34 * scale
    rowsn = (len(cells) + cols - 1) // cols
    Wt = cols * (cw + gap)
    Ht = rowsn * (cw + gap)
    cv = [[25] * Wt for _ in range(Ht)]
    for n, c in enumerate(cells):
        px = (n % cols) * (cw + gap)
        py = (n // cols) * (cw + gap)
        for yy in range(cw):
            for xx in range(cw):
                cv[py + yy][px + xx] = c[yy // scale][xx // scale]
    png_gray(cv, 1, path)


vp = Vpp(os.path.join(G, "patch.vpp_pc"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
A_patch = vp.rd(vp.find("fnt_chinese", "g_peg_pc"))
A_tex = vt.rd(vt.find("fnt_chinese"))
VFp = vp.rd(vp.find("fnt_chinese", "vf3_pc"))

b = vp.rd(vp.find("charlist_CH", "txt"))
m = re.search(rb"count\s*=\s*(\d+)", b)
body = b[m.end():] if m else b
end = body.find(b"//ENDOFFILE")
OFF = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


def uv(k):
    N = struct.unpack_from("<I", VFp, 8)[0]
    U = 0xD0 + N * 16
    V = U + N * 4
    return (struct.unpack_from("<i", VFp, U + k * 4)[0],
            struct.unpack_from("<i", VFp, V + k * 4)[0])


# 22 组：(原字, J) —— J = 引擎输出索引 = 显示字在 charlist 里的位置
PAIRS = [("交", 287), ("他", 301), ("你", 336), ("保", 354), ("們", 362),
         ("兄", 410), ("免", 417), ("到", 458), ("去", 535), ("受", 543),
         ("弟", 967), ("擊", 1221), ("攻", 1243), ("易", 1292), ("正", 1458),
         ("的", 1784), ("要", 2268), ("護", 2342), ("行", 2372), ("進", 2491),
         ("避", 2514), ("需", 2656)]

print("原字  charlist.index  源格子(idx-5)  目标格子(J-5)  源格应显示  目标格应显示")
src_cells, dst_cells = [], []
for c, J in PAIRS:
    i = OFF.index(ord(c))
    s, dd = i - OFFSET, J - OFFSET
    print("  %s      %-6d        %-6d         %-6d       %s          %s" % (
        c, i, s, dd, chr(OFF[i]), chr(OFF[J])))
    us, vs = uv(s)
    ud, vd = uv(dd)
    src_cells.append(crop(A_patch, us - 2, vs - 2))
    dst_cells.append(crop(A_patch, ud - 2, vd - 2))
sheet(src_cells, path=r"F:/sr2-cn/_KH_src.png")
sheet(dst_cells, path=r"F:/sr2-cn/_KH_dst.png")
print("\n_KH_src.png = 源格子（应读出 22 个原字）")
print("_KH_dst.png = 目标格子（应读出 22 个错误显示的字）")
