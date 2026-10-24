# -*- coding: utf-8 -*-
# 用墨迹列剖面精确找图集字形边界，并与 vf3 的 U 值对齐（标定 ASCII 行 + CJK 行）
import os, struct, re, hashlib

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


def block(d, bx, by):
    o = (by * BW + bx) * 16
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
    px = []
    for py in range(4):
        row = []
        for pxx in range(4):
            k = py * 4 + pxx
            r, g, bl = pal[(idx >> (2 * k)) & 3]
            row.append((r * 299 + g * 587 + bl * 114) // 1000)
        px.append(row)
    return px


def band_profile(d, y0, y1, x0=0, x1=2048):
    """返回每个 x 的墨迹强度（该列在 y0..y1 内的最大亮度）"""
    prof = [0] * (x1 - x0)
    cache = {}
    for X in range(x0, x1):
        mx = 0
        for Y in range(y0, y1):
            bx, by = X // 4, Y // 4
            key = (bx, by)
            if key not in cache:
                cache[key] = block(d, bx, by)
            v = cache[key][Y % 4][X % 4]
            if v > mx:
                mx = v
        prof[X - x0] = mx
    return prof


def segs(prof, thr=40, minw=3):
    out = []
    st = None
    for i, v in enumerate(prof):
        if v > thr and st is None:
            st = i
        elif v <= thr and st is not None:
            if i - st >= minw:
                out.append((st, i - 1))
            st = None
    if st is not None:
        out.append((st, len(prof) - 1))
    return out


vp = Vpp(os.path.join(G, "patch.vpp_pc"))
vc = Vpp(os.path.join(G, "common.vpp_pc"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
A_patch = vp.rd(vp.find("fnt_chinese", "g_peg_pc"))
A_tex = vt.rd(vt.find("fnt_chinese"))
VFp = vp.rd(vp.find("fnt_chinese", "vf3_pc"))
VFc = vc.rd(vc.find("fnt_chinese", "vf3_pc"))
print("atlas patch md5=%s" % hashlib.md5(A_patch).hexdigest())
print("atlas tex   md5=%s" % hashlib.md5(A_tex).hexdigest())
print("vf3 patch md5=%s" % hashlib.md5(VFp).hexdigest())
print("vf3 comm  md5=%s" % hashlib.md5(VFc).hexdigest())


def uvv(vf, k):
    N = struct.unpack_from("<I", vf, 8)[0]
    U = 0xD0 + N * 16
    V = U + N * 4
    return (struct.unpack_from("<i", vf, U + k * 4)[0],
            struct.unpack_from("<i", vf, V + k * 4)[0])


b = vp.rd(vp.find("charlist_CH", "txt"))
m = re.search(rb"count\s*=\s*(\d+)", b)
body = b[m.end():] if m else b
end = body.find(b"//ENDOFFILE")
OFF = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]

print("\n=== vf3 的 U/V 样本 ===")
for k in [0, 1, 2, 3, 5, 10, 30, 33, 36, 90, 94, 95, 96]:
    up, vp2 = uvv(VFp, k)
    uc, vc2 = uvv(VFc, k)
    print("  idx %-4d patch=(%4d,%3d)  common=(%4d,%3d)  char=%s" % (k, up, vp2, uc, vc2, chr(OFF[k])))

print("\n=== ASCII 行 (y=0..30) 墨迹分段，与 vf3 的 U 对齐 ===")
for tag, d in (("patch", A_patch), ("tex", A_tex)):
    prof = band_profile(d, 0, 30, 0, 1100)
    s = segs(prof)
    print("  [%s] 前 20 段: %s" % (tag, s[:20]))
print("  vf3(patch) U[0..20] =", [uvv(VFp, k)[0] for k in range(0, 21)])
print("  vf3(comm ) U[0..20] =", [uvv(VFc, k)[0] for k in range(0, 21)])

print("\n=== CJK 行：idx 325..389 所在行 (vf3 V=125) 墨迹分段 ===")
for tag, d in (("patch", A_patch), ("tex", A_tex)):
    prof = band_profile(d, 125, 156, 0, 2048)
    s = segs(prof, thr=40, minw=8)
    print("  [%s] 共 %d 段，前 12 段: %s" % (tag, len(s), s[:12]))
print("  vf3(patch) U[325..341] =", [uvv(VFp, k)[0] for k in range(325, 342)])
print("  vf3(patch) U[389] =", uvv(VFp, 389)[0])
