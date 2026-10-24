# -*- coding: utf-8 -*-
# 验证换算：vf3 的 (U,V) 与图集格子的关系 = (U-248, V+31)，图集是 65 列 / 行距 31 / 原点(1,1)
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


def crop(d, x, y, w=31, h=31):
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


def sheet(cells, scale=5, cols=11, gap=5, path="s.png"):
    cw = 31 * scale
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
vc = Vpp(os.path.join(G, "common.vpp_pc"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
A_patch = vp.rd(vp.find("fnt_chinese", "g_peg_pc"))
A_tex = vt.rd(vt.find("fnt_chinese"))
VFp = vp.rd(vp.find("fnt_chinese", "vf3_pc"))
VFc = vc.rd(vc.find("fnt_chinese", "vf3_pc"))

b = vp.rd(vp.find("charlist_CH", "txt"))
m = re.search(rb"count\s*=\s*(\d+)", b)
body = b[m.end():] if m else b
end = body.find(b"//ENDOFFILE")
OFF = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
B = None
import glob
for q in [r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2"]:
    if os.path.exists(q):
        vv = Vpp(q)
        bb = vv.rd(vv.find("charlist_CH", "txt"))
        mm = re.search(rb"count\s*=\s*(\d+)", bb)
        bd = bb[mm.end():] if mm else bb
        e2 = bd.find(b"//ENDOFFILE")
        B = [int(x) for x in re.findall(rb"\d+", bd[:e2 if e2 > 0 else None])]
print("OFF=%d  B(2795表)=%s" % (len(OFF), len(B) if B else "无"))


def uvv(vf, k):
    N = struct.unpack_from("<I", vf, 8)[0]
    U = 0xD0 + N * 16
    V = U + N * 4
    return (struct.unpack_from("<i", vf, U + k * 4)[0],
            struct.unpack_from("<i", vf, V + k * 4)[0])


IDXS = [333, 336, 354, 362, 371, 410, 967, 1784, 1836, 2342, 2656]
print("\n换算验证：cell = (U-248, V+31)，与 65 列网格 (1+31*(k%65), 1+31*(k//65)) 对比")
cells_p = []
cells_t = []
for k in IDXS:
    u, v = uvv(VFp, k)
    cx, cy = u - 248, v + 31
    gx, gy = 1 + 31 * (k % 65), 1 + 31 * (k // 65)
    lab = ("B[%d]=%s" % (k, chr(B[k]))) if (B and k < len(B)) else ("OFF[%d]=%s" % (k, chr(OFF[k])))
    print("  idx %-5d vf3=(%4d,%4d) -> cell=(%4d,%4d)   网格=(%4d,%4d)  %s  %s" % (
        k, u, v, cx, cy, gx, gy, lab, "一致" if (cx, cy) == (gx, gy) else "<<<不一致"))
    cells_p.append(crop(A_patch, cx, cy))
    cells_t.append(crop(A_tex, cx, cy))
sheet(cells_p, path=r"F:/sr2-cn/_KE_patch_cells.png")
sheet(cells_t, path=r"F:/sr2-cn/_KE_tex_cells.png")
print("\n顺序:", IDXS)
print("已保存 _KE_patch_cells.png / _KE_tex_cells.png")
