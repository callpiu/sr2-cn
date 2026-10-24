# -*- coding: utf-8 -*-
# 视觉验证修复后的图集 + 同时构建 textures 图集的修复（偏移 +11）
import os, re, struct, zlib, hashlib

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
BW = 2048 // 4
CELL = 31


class Vpp:
    def __init__(self, path, only_header=False):
        self.path = path
        self.f = open(path, "rb")
        head = self.f.read(0x2000)
        o = 5 + 0x14F
        self.num = struct.unpack_from("<i", head, o)[0]
        self.lo = struct.unpack_from("<i", head, o + 8)[0]
        self.lf = struct.unpack_from("<i", head, o + 12)[0]
        self.le = struct.unpack_from("<i", head, o + 16)[0]
        self.na = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ea = ((self.na + self.lf) & 0xFFFFF800) + 0x800
        self.ds = ((self.ea + self.le) & 0xFFFFF800) + 0x800

    def z(self, b, p):
        e = b.find(b"\x00", p)
        return b[p:e].decode("ascii", "replace")

    def ents(self):
        self.f.seek(0)
        meta = self.f.read(max(self.ea + self.le, 0x800 + self.num * 28) + 0x1000)
        r = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b_, c, dd, ln = struct.unpack_from("<IIiii", meta, e)
            r.append(dict(idx=i, n=self.z(meta, self.na + a),
                          x=self.z(meta, self.ea + b_) if b_ else "", o=dd, z=ln, eo=e))
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


def dec_block(buf, off):
    b = buf[off:off + 16]
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
    out = []
    for py in range(4):
        row = []
        for pxx in range(4):
            k = py * 4 + pxx
            a4 = (b[k // 2] >> (4 * (k % 2))) & 0xF
            r, g, bl = pal[(idx >> (2 * k)) & 3]
            row.append((r, g, bl, a4 * 17))
        out.append(row)
    return out


def enc_block(px):
    ab = bytearray(8)
    for py in range(4):
        for pxx in range(4):
            k = py * 4 + pxx
            a4 = max(0, min(15, px[py][pxx][3] >> 4))
            ab[k // 2] |= a4 << (4 * (k % 2))
    mx = max(px[py][pxx][3] for py in range(4) for pxx in range(4))
    lum = min(mx, 248)
    v5 = max(0, min(31, lum >> 3))
    v6 = max(0, min(63, lum >> 2))
    grey = (v5 << 11) | (v6 << 5) | v5
    L = max(lum, 1)
    t1, t2 = 2.0 * L / 3.0, L / 3.0
    words = 0
    for py in range(4):
        for pxx in range(4):
            k = py * 4 + pxx
            q = float(px[py][pxx][3])
            cands = [abs(q - L), abs(q - t1), abs(q - t2)]
            pick = cands.index(min(cands))
            ii = 0 if pick == 0 else (2 if pick == 1 else 3)
            words |= (ii & 3) << (2 * k)
    out = bytearray(16)
    out[0:8] = ab
    out[8] = grey & 0xFF
    out[9] = (grey >> 8) & 0xFF
    out[12] = words & 0xFF
    out[13] = (words >> 8) & 0xFF
    out[14] = (words >> 16) & 0xFF
    out[15] = (words >> 24) & 0xFF
    return bytes(out)


def get_px(atl, X, Y):
    o = ((Y // 4) * BW + X // 4) * 16
    return dec_block(atl, o)[Y % 4][X % 4]


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
    cv = [[25] * (cols * (cw + gap)) for _ in range(rowsn * (cw + gap))]
    for n, c in enumerate(cells):
        px = (n % cols) * (cw + gap)
        py = (n // cols) * (cw + gap)
        for yy in range(cw):
            for xx in range(cw):
                cv[py + yy][px + xx] = c[yy // scale][xx // scale]
    png_gray(cv, 1, path)


def crop34(atl, X, Y):
    return [[get_px(atl, X + xx, Y + yy)[3] for xx in range(34)] for yy in range(34)]


# --- charlist & vf3（从原版 patch 取） ---
vp0 = Vpp(os.path.join(G, "patch.vpp_pc"))
vf_e = vp0.find("fnt_chinese", "vf3_pc")
vf = vp0.read_at(vp0.ds + vf_e["o"], vf_e["z"])
N = struct.unpack_from("<I", vf, 8)[0]
UOFF = 0xD0 + N * 16
VOFF = UOFF + N * 4


def uv(k):
    return (struct.unpack_from("<i", vf, UOFF + k * 4)[0],
            struct.unpack_from("<i", vf, VOFF + k * 4)[0])


cl_e = vp0.find("charlist_CH", "txt")
cb = vp0.read_at(vp0.ds + cl_e["o"], cl_e["z"])
m = re.search(rb"count\s*=\s*(\d+)", cb)
body = cb[m.end():] if m else cb
end = body.find(b"//ENDOFFILE")
OFF = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]

PAIRS = [("交", 287), ("他", 301), ("你", 336), ("保", 354), ("們", 362),
         ("兄", 410), ("免", 417), ("到", 458), ("去", 535), ("受", 543),
         ("弟", 967), ("擊", 1221), ("攻", 1243), ("易", 1292), ("正", 1458),
         ("的", 1784), ("要", 2268), ("護", 2342), ("行", 2372), ("進", 2491),
         ("避", 2514), ("需", 2656)]

# --- 1) 已修好的 patch 图集：裁目标格子 ---
vf_fixed = Vpp(r"F:/sr2-cn/_FIX/patch.vpp_pc")
at_fixed = vf_fixed.read_at(vp0.ds + vp0.find("fnt_chinese", "g_peg_pc")["o"], 4194304)
cells = [crop34(at_fixed, uv(J - 5)[0] - 2, uv(J - 5)[1] - 2) for _, J in PAIRS]
sheet(cells, path=r"F:/sr2-cn/_KJ_fixed_patch.png")
print("已保存 _KJ_fixed_patch.png（patch 图集修复后，目标格子应读出 22 个正确字）")

# --- 2) textures 图集：偏移 +11，构建并裁目标格子 ---
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
te = vt.find("fnt_chinese")
at_tex = vt.read_at(vt.ds + te["o"], te["z"])
print("textures 图集 size=%d md5=%s" % (len(at_tex), hashlib.md5(at_tex).hexdigest()))
TEXOFF = 11
out = bytearray(at_tex)
for c, J in PAIRS:
    i = OFF.index(ord(c))
    s, dd = i - TEXOFF, J - TEXOFF
    us, vs = uv(s)
    ud, vd = uv(dd)
    srcpx = [[get_px(at_tex, us + xx, vs + yy) for xx in range(CELL)] for yy in range(CELL)]
    for by in range(vd // 4, (vd + CELL - 1) // 4 + 1):
        for bx in range(ud // 4, (ud + CELL - 1) // 4 + 1):
            o = (by * BW + bx) * 16
            blk = [list(r) for r in dec_block(at_tex, o)]
            for yy in range(4):
                Y = by * 4 + yy
                if not (vd <= Y < vd + CELL):
                    continue
                for xx in range(4):
                    X = bx * 4 + xx
                    if ud <= X < ud + CELL:
                        blk[yy][xx] = srcpx[Y - vd][X - ud]
            out[(by * BW + bx) * 16:(by * BW + bx) * 16 + 16] = enc_block(blk)
os.makedirs(r"F:/sr2-cn/_FIX", exist_ok=True)
open(r"F:/sr2-cn/_FIX/tex_fnt_chinese_fixed.bin", "wb").write(bytes(out))
print("已保存 _FIX/tex_fnt_chinese_fixed.bin  md5=%s" % hashlib.md5(bytes(out)).hexdigest())
cells2 = [crop34(bytes(out), uv(J - TEXOFF)[0] - 2, uv(J - TEXOFF)[1] - 2) for _, J in PAIRS]
sheet(cells2, path=r"F:/sr2-cn/_KJ_fixed_tex.png")
print("已保存 _KJ_fixed_tex.png")
