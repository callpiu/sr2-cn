# -*- coding: utf-8 -*-
# 为 22 个目标字裁出「正确字形来源」格子（在汉化表 B 里 -> 用 patch 图集；不在 B -> 用 textures 原图集）
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
            r.append(dict(n=self.z(self.na, a), x=self.z(self.ea, b_) if b_ else "", o=dd, z=ln, eo=e))
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
CELLS_COLS, PITCH, X0, Y0, ASCII_N = 65, 31, 1, 1, 0


def cell_xy(index):
    return X0 + PITCH * (index % CELLS_COLS), Y0 + PITCH * (index // CELLS_COLS)


def rgb565(v):
    return (((v >> 11) & 0x1F) * 255 // 31, ((v >> 5) & 0x3F) * 255 // 63, (v & 0x1F) * 255 // 31)


def dec_px(d, X, Y):
    bx, by = X // 4, Y // 4
    o = (by * BW + bx) * 16
    b = d[o:o + 16]
    if len(b) < 16:
        return 0
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


def sheet(cells, scale=4, cols=6, gap=6, path="s.png"):
    cw = 31 * scale
    rowsn = (len(cells) + cols - 1) // cols
    Wt = cols * (cw + gap)
    Ht = rowsn * (cw + gap)
    cv = [[0] * Wt for _ in range(Ht)]
    for n, c in enumerate(cells):
        px = (n % cols) * (cw + gap)
        py = (n // cols) * (cw + gap)
        for yy in range(cw):
            for xx in range(cw):
                cv[py + yy][px + xx] = c[yy // scale][xx // scale]
    png_gray(cv, 1, path)


PAIRS = [("交", "乱"), ("他", "亡"), ("你", "任"), ("保", "伪"), ("們", "位"),
         ("兄", "偶"), ("免", "像"), ("到", "冰"), ("去", "勾"), ("受", "匪"),
         ("弟", "巧"), ("擊", "拮"), ("攻", "挺"), ("易", "携"), ("正", "校"),
         ("的", "璨"), ("要", "衡"), ("護", "该"), ("進", "远"), ("避", "通"),
         ("需", "雄")]

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
A = vp.rd(vp.find("fnt_chinese", "g_peg_pc"))
OFF = load_cl(vp)
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
T = vt.rd(vt.find("fnt_chinese"))
B = load_cl(Vpp(r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2"))

print("atlas patch=%d  atlas textures=%d" % (len(A), len(T)))
print("\n%-4s %-6s %-8s %-8s %s" % ("字", "引擎idx", "B idx", "OFF idx", "字形来源"))
plan = []
for c, disp in PAIRS:
    cp = ord(c)
    e = B.index(ord(disp))
    if cp in B:
        src = B.index(cp); srctag = "patch@%d" % src; atlas = "A"
    else:
        src = OFF.index(cp); srctag = "textures@%d" % src; atlas = "T"
    plan.append((c, cp, e, src, atlas))
    print("%-4s %-7d %-8s %-8d %s" % (c, e, B.index(cp) if cp in B else "—", OFF.index(cp), srctag))

# 裁出源字形 + 目标当前字形（对比）
srcs = []
dsts = []
for c, cp, e, src, atlas in plan:
    d = A if atlas == "A" else T
    x, y = cell_xy(src)
    srcs.append(crop(d, x, y))
    x2, y2 = cell_xy(e)
    dsts.append(crop(A, x2, y2))
sheet(srcs, path=r"F:/sr2-cn/_JQ_src.png")
sheet(dsts, path=r"F:/sr2-cn/_JQ_dst.png")
print("\n已保存 _JQ_src.png（正确字形来源）与 _JQ_dst.png（引擎当前会渲染的）")
