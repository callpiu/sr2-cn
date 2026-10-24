# -*- coding: utf-8 -*-
"""构建字形修复补丁：把 22 个字的「源格子」搬进「引擎会去取的目标格子」

原理（已逐格视觉验证）：
  · vf3 的 (U[k],V[k]) 就是图集第 k 格的左上角
  · 图集字形顺序比 charlist_CH 偏移 +5：第 k 格 = charlist[k+5]
  · 引擎渲染字符 c 时取到的格子 = J(c)-5，那一格现在装着错误的字形
  · 所以：把 第 (charlist.index(c)-5) 格 复制到 第 (J(c)-5) 格

输出：F:/sr2-cn/_FIX/patch.vpp_pc（不动游戏）
"""
import os, re, struct, zlib, hashlib, shutil

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
OFFSET = 5
OUTDIR = r"F:/sr2-cn/_FIX"


class Vpp:
    def __init__(self, path):
        self.d = bytearray(open(path, "rb").read())
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
            r.append(dict(idx=i, n=self.z(self.na, a), x=self.z(self.ea, b_) if b_ else "", o=dd, z=ln, eo=e))
        return r

    def find(self, n, x=None):
        for e in self.ents():
            if e["n"].lower() == n.lower() and (x is None or e["x"].lower() == x.lower()):
                return e
        return None


# ---------------- DXT3 (BC2) 纯 Python ----------------
def rgb565(v):
    return (((v >> 11) & 0x1F) * 255 // 31, ((v >> 5) & 0x3F) * 255 // 63, (v & 0x1F) * 255 // 31)


def dec_block(buf, off):
    """返回 4x4 的 (r,g,b,a)"""
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
        for px in range(4):
            k = py * 4 + px
            a4 = (b[k // 2] >> (4 * (k % 2))) & 0xF
            r, g, bl = pal[(idx >> (2 * k)) & 3]
            row.append((r, g, bl, a4 * 17))
        out.append(row)
    return out


def enc_block(px):
    """px = 4x4 的 (r,g,b,a) -> 16 字节；复刻 sr2lib 的编码方式（预乘灰度）"""
    # 4bit alpha
    ab = bytearray(8)
    for py in range(4):
        for pxx in range(4):
            k = py * 4 + pxx
            a4 = max(0, min(15, px[py][pxx][3] >> 4))
            ab[k // 2] |= a4 << (4 * (k % 2))
    mx = 0
    for py in range(4):
        for pxx in range(4):
            if px[py][pxx][3] > mx:
                mx = px[py][pxxx] if False else px[py][pxx][3]
    lum = min(mx, 248)
    v5 = max(0, min(31, lum >> 3))
    v6 = max(0, min(63, lum >> 2))
    grey = (v5 << 11) | (v6 << 5) | v5
    L = max(lum, 1)
    t1 = 2.0 * L / 3.0
    t2 = L / 3.0
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
    out[10] = 0
    out[11] = 0
    out[12] = words & 0xFF
    out[13] = (words >> 8) & 0xFF
    out[14] = (words >> 16) & 0xFF
    out[15] = (words >> 24) & 0xFF
    return bytes(out)


BW = 2048 // 4
CELL = 31

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
e_atlas = vp.find("fnt_chinese", "g_peg_pc")
atlas_off = vp.ds + e_atlas["o"]
atlas = bytes(vp.d[atlas_off:atlas_off + e_atlas["z"]])
print("图集: patch.vpp_pc @0x%X size=%d md5=%s" % (atlas_off, len(atlas), hashlib.md5(atlas).hexdigest()))

vf = vp.d[vp.ds + vp.find("fnt_chinese", "vf3_pc")["o"]:]
vf = bytes(vf[:vp.find("fnt_chinese", "vf3_pc")["z"]])
N = struct.unpack_from("<I", vf, 8)[0]
UOFF = 0xD0 + N * 16
VOFF = UOFF + N * 4


def uv(k):
    return (struct.unpack_from("<i", vf, UOFF + k * 4)[0],
            struct.unpack_from("<i", vf, VOFF + k * 4)[0])


b = vp.d[vp.ds + vp.find("charlist_CH", "txt")["o"]:]
cl_e = vp.find("charlist_CH", "txt")
b = bytes(vp.d[vp.ds + cl_e["o"]:vp.ds + cl_e["o"] + cl_e["z"]])
m = re.search(rb"count\s*=\s*(\d+)", b)
body = b[m.end():] if m else b
end = body.find(b"//ENDOFFILE")
OFF = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]

PAIRS = [("交", 287), ("他", 301), ("你", 336), ("保", 354), ("們", 362),
         ("兄", 410), ("免", 417), ("到", 458), ("去", 535), ("受", 543),
         ("弟", 967), ("擊", 1221), ("攻", 1243), ("易", 1292), ("正", 1458),
         ("的", 1784), ("要", 2268), ("護", 2342), ("行", 2372), ("進", 2491),
         ("避", 2514), ("需", 2656)]


def get_px(atl, X, Y):
    o = ((Y // 4) * BW + X // 4) * 16
    return dec_block(atl, o)[Y % 4][X % 4]


def put_block(buf, bx, by, px):
    o = (by * BW + bx) * 16
    buf[o:o + 16] = enc_block(px)


out = bytearray(atlas)
jobs = []
for c, J in PAIRS:
    i = OFF.index(ord(c))
    s, dd = i - OFFSET, J - OFFSET
    us, vs = uv(s)
    ud, vd = uv(dd)
    # 读源格子像素
    srcpx = [[get_px(atlas, us + xx, vs + yy) for xx in range(CELL)] for yy in range(CELL)]
    # 写入目标格子：只重编受影响块，块内格外的像素保持原样
    bx0, bx1 = ud // 4, (ud + CELL - 1) // 4
    by0, by1 = vd // 4, (vd + CELL - 1) // 4
    for by in range(by0, by1 + 1):
        for bx in range(bx0, bx1 + 1):
            o = (by * BW + bx) * 16
            blk = [list(r) for r in dec_block(atlas, o)]
            for yy in range(4):
                Y = by * 4 + yy
                if not (vd <= Y < vd + CELL):
                    continue
                for xx in range(4):
                    X = bx * 4 + xx
                    if not (ud <= X < ud + CELL):
                        continue
                    blk[yy][xx] = srcpx[Y - vd][X - ud]
            put_block(out, bx, by, blk)
    jobs.append((c, J, i, s, dd, (us, vs), (ud, vd)))

print("\n共 %d 处替换：" % len(jobs))
for c, J, i, s, dd, sv, dv in jobs:
    print("  %s: charlist[%d] 格%d(%d,%d) -> 格%d(%d,%d)" % (c, i, s, sv[0], sv[1], dd, dv[0], dv[1]))

newmd5 = hashlib.md5(bytes(out)).hexdigest()
print("\n新图集 md5 = %s   (大小 %d，与原图集相同)" % (newmd5, len(out)))
assert len(out) == len(atlas)

# 写回 vpp 副本
os.makedirs(OUTDIR, exist_ok=True)
vp.d[atlas_off:atlas_off + len(atlas)] = out
dst = os.path.join(OUTDIR, "patch.vpp_pc")
open(dst, "wb").write(bytes(vp.d))
print("已输出: %s  (%d 字节, md5=%s)" % (dst, len(vp.d), hashlib.md5(bytes(vp.d)).hexdigest()))

# 验证：重读新图集，裁目标格子
chk = Vpp(dst)
atlas2 = bytes(chk.d[atlas_off:atlas_off + e_atlas["z"]])
ok = 0
print("\n验证目标格子现在的字形（应变成正确字）：")
for c, J, i, s, dd, sv, dv in jobs:
    # 只统计非空格像素是否与源格子一致
    same = 0
    tot = 0
    for yy in range(0, CELL, 2):
        for xx in range(0, CELL, 2):
            a = get_px(atlas2, uv(dd)[0] + xx, uv(dd)[1] + yy)
            bb2 = get_px(atlas, uv(s)[0] + xx, uv(s)[1] + yy)
            tot += 1
            if abs(a[3] - bb2[3]) <= 34:
                same += 1
    ok += (same == tot)
    print("  %s : 一致度 %d/%d" % (c, same, tot))
print("\n完全一致的格子: %d/%d" % (ok, len(jobs)))
