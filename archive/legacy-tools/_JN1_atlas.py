# -*- coding: utf-8 -*-
# 定位 fnt_chinese 图集 + 解析 vf3 头部/记录/U表/V表
import os, re, struct, zlib, glob

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
            r.append(dict(n=self.z(self.na, a), x=self.z(self.ea, b_) if b_ else "", o=dd, z=ln))
        return r

    def rd(self, e):
        p = self.ds + e["o"]
        return self.d[p:p + e["z"]]

    def find(self, n, x=None):
        for e in self.ents():
            if e["n"].lower() == n.lower() and (x is None or e["x"].lower() == x.lower()):
                return e
        return None


print("=== 搜索 fnt_chinese_nobdr 图集 ===")
for fn in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    v = Vpp(fn)
    for e in v.ents():
        if "fnt_chinese" in e["n"].lower():
            print("  %-14s %-34s .%-8s size=%d" % (os.path.basename(fn), e["n"], e["x"], e["z"]))

v = Vpp(os.path.join(G, "patch.vpp_pc"))
b = v.rd(v.find("fnt_chinese", "vf3_pc"))
print("\n=== vf3 头部 0x00-0xD8 ===")
for i in range(0, 0xD8, 16):
    print("  %04X: %s" % (i, b[i:i + 16].hex(" ")))

N = struct.unpack_from("<I", b, 8)[0]
print("\nN =", N, " 文件大小 =", len(b), "=0x%X" % len(b))

print("\n=== 记录区（从 0xD0 起，每 16 字节）前 4 条 ===")
for i in range(4):
    off = 0xD0 + i * 16
    print("  rec[%d] @0x%X: %s  -> <4H=%s  <4f=%s" % (
        i, off, b[off:off + 16].hex(" "),
        struct.unpack_from("<4H", b, off),
        tuple(round(x, 1) for x in struct.unpack_from("<4f", b, off))))

U_OFF = 0xD0 + N * 16
V_OFF = U_OFF + N * 4
print("\nU 表 @0x%X  V 表 @0x%X  文件末尾 0x%X  (V表需 %d 字节, 实际 %d)" % (
    U_OFF, V_OFF, len(b), N * 4, len(b) - V_OFF))

print("\n=== U/V 表在关键索引处的值 ===")
for i in [287, 302, 333, 336, 350, 354, 358, 362, 371, 405, 410, 962, 967, 1784, 1787]:
    if i < N:
        u = struct.unpack_from("<I", b, U_OFF + i * 4)[0]
        vv = struct.unpack_from("<I", b, V_OFF + i * 4)[0] if V_OFF + i * 4 + 4 <= len(b) else None
        print("  idx %-5d U=%-10d V=%s" % (i, u, vv))


# TGA -> PNG
def tga_to_png(data, out):
    idl, cmt, typ = data[0], data[1], data[2]
    w, h, dep = struct.unpack_from("<HHB", data, 12)
    p = 18 + idl
    if typ not in (2, 10):
        return None, "type=%d 不支持" % typ
    px = bytearray()
    bpp = dep // 8
    total = w * h
    if typ == 2:
        px = bytearray(data[p:p + total * bpp])
    else:
        i = 0
        while i < total:
            hd = data[p]; p += 1
            n = (hd & 0x7F) + 1
            if hd & 0x80:
                val = data[p:p + bpp]; p += bpp
                for _ in range(n):
                    px += val
            else:
                px += data[p:p + n * bpp]; p += n * bpp
            i += n
    rows = []
    for y in range(h):
        src = (h - 1 - y) * w * bpp
        row = bytearray(b"\x00")
        for x in range(w):
            o = src + x * bpp
            if bpp >= 3:
                row += bytes([px[o + 2], px[o + 1], px[o]])
            else:
                row += bytes([px[o]] * 3)
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(tag, data_):
        c = tag + data_
        return struct.pack(">I", len(data_)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6))
    png += chunk(b"IEND", b"")
    open(out, "wb").write(png)
    return (w, h), None


e = v.find("fnt_chinese_nobdr", "tga")
if not e:
    print("\n图集不在 patch.vpp_pc")
    for fn in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
        vv = Vpp(fn)
        ee = vv.find("fnt_chinese_nobdr", "tga")
        if ee:
            print("  在 %s  size=%d" % (fn, ee["z"]))
            d = vv.rd(ee)
            print("  head:", d[:20].hex(" "))
            info, err = tga_to_png(d, r"F:/sr2-cn/_ATLAS_chinese.png")
            print("  转换:", info, err)
            break
else:
    d = v.rd(e)
    print("\n图集在 patch.vpp_pc size=%d head=%s" % (len(d), d[:20].hex(" ")))
    info, err = tga_to_png(d, r"F:/sr2-cn/_ATLAS_chinese.png")
    print("  转换:", info, err)
