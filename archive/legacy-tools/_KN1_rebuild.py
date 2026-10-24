# -*- coding: utf-8 -*-
"""重建修复补丁（修正「行」，加入标点「，」），验证并部署"""
import os, re, struct, zlib, hashlib, shutil, subprocess

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
ORIG = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
OUTDIR = r"F:/sr2-cn/_FIX"
OFFSET = 5
BW = 2048 // 4
CELL = 31


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
        e = self.d.find(b"\x00", p)
        return self.d[p:e].decode("ascii", "replace")

    def ents(self):
        r = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b_, c, dd, ln = struct.unpack_from("<IIiii", self.d, e)
            r.append(dict(idx=i, n=self.z(self.d, self.na + a),
                          x=self.z(self.d, self.ea + b_) if b_ else "", o=dd, z=ln))
        return r

    def find(self, n, x=None):
        for e in self.ents():
            if e["n"].lower() == n.lower() and (x is None or e["x"].lower() == x.lower()):
                return e
        return None


vp = Vpp(ORIG)
at_off = vp.ds + vp.find("fnt_chinese", "g_peg_pc")["o"]
atlas = bytes(vp.d[at_off:at_off + 4194304])
vf_e = vp.find("fnt_chinese", "vf3_pc")
vf = bytes(vp.d[vp.ds + vf_e["o"]:vp.ds + vf_e["o"] + vf_e["z"]])
N = struct.unpack_from("<I", vf, 8)[0]
UOFF = 0xD0 + N * 16
VOFF = UOFF + N * 4


def uv(k):
    return (struct.unpack_from("<i", vf, UOFF + k * 4)[0],
            struct.unpack_from("<i", vf, VOFF + k * 4)[0])


cle = vp.find("charlist_CH", "txt")
cl = bytes(vp.d[vp.ds + cle["o"]:vp.ds + cle["o"] + cle["z"]])
m = re.search(rb"count\s*=\s*(\d+)", cl)
body = cl[m.end():] if m else cl
end = body.find(b"//ENDOFFILE")
OFF = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]

# 23 组：22 个原字（「行」修正为 J=2234） + 标点「，」
PAIRS = [("交", 287), ("他", 301), ("你", 336), ("保", 354), ("們", 362),
         ("兄", 410), ("免", 417), ("到", 458), ("去", 535), ("受", 543),
         ("弟", 967), ("擊", 1221), ("攻", 1243), ("易", 1292), ("正", 1458),
         ("的", 1784), ("要", 2268), ("護", 2342), ("行", 2234), ("進", 2491),
         ("避", 2514), ("需", 2656), ("，", 2809)]


def get_px(atl, X, Y):
    return dec_block(atl, ((Y // 4) * BW + X // 4) * 16)[Y % 4][X % 4]


out = bytearray(atlas)
print("共 %d 处替换：" % len(PAIRS))
for c, J in PAIRS:
    i = OFF.index(ord(c))
    s, dd = i - OFFSET, J - OFFSET
    us, vs = uv(s)
    ud, vd = uv(dd)
    srcpx = [[get_px(atlas, us + xx, vs + yy) for xx in range(CELL)] for yy in range(CELL)]
    for by in range(vd // 4, (vd + CELL - 1) // 4 + 1):
        for bx in range(ud // 4, (ud + CELL - 1) // 4 + 1):
            o = (by * BW + bx) * 16
            blk = [list(r) for r in dec_block(atlas, o)]
            for yy in range(4):
                Y = by * 4 + yy
                if not (vd <= Y < vd + CELL):
                    continue
                for xx in range(4):
                    X = bx * 4 + xx
                    if ud <= X < ud + CELL:
                        blk[yy][xx] = srcpx[Y - vd][X - ud]
            out[o:o + 16] = enc_block(blk)
    print("  %s: 源格 %-5d(%4d,%3d) -> 目标格 %-5d(%4d,%3d)  [charlist[%d]=%s]" % (
        c, s, us, vs, dd, ud, vd, J, chr(OFF[J])))

os.makedirs(OUTDIR, exist_ok=True)
vp.d[at_off:at_off + 4194304] = out
dst = os.path.join(OUTDIR, "patch.vpp_pc")
open(dst, "wb").write(bytes(vp.d))
newmd5 = hashlib.md5(bytes(vp.d)).hexdigest()
print("\n新 patch.vpp_pc md5 = %s  (%d 字节)" % (newmd5, len(vp.d)))

# 部署
try:
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="ignore").stdout.lower()
except Exception:
    tl = ""
if "sr2_pc.exe" in tl:
    print("!!! 游戏正在运行，未部署。请退出游戏后重跑本脚本。")
    raise SystemExit(1)
cur = hashlib.md5(open(os.path.join(G, "patch.vpp_pc"), "rb").read()).hexdigest()
print("当前游戏 patch.vpp_pc md5 = %s" % cur)
shutil.copy2(dst, os.path.join(G, "patch.vpp_pc"))
print("已部署 ✓  部署后 md5 = %s" % hashlib.md5(open(os.path.join(G, "patch.vpp_pc"), "rb").read()).hexdigest())
print("\n回退：cp \"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017\" \"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc\"")
