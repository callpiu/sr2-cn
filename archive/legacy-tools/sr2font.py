# -*- coding: utf-8 -*-
"""
sr2font.py —— Saints Row 2 字体图集字形错位修复工具库（纯 Python，无第三方依赖）

原理
----
游戏把文字存成「字符表索引」(charlist_CH.txt)，渲染时：
    字符 c -> 引擎索引 E(c) -> 图集第 E(c) 格 -> 画出该格里的字形
官方数据里 **图集的字形排列顺序与 charlist_CH.txt 不一致**（整体错位若干位），
于是 E(c) 指向的那一格装的是别的字 -> 乱码。

关键事实（本项目逐格视觉验证过）
--------------------------------
1. vf3 文件尾部的两个数组就是每格的**左上角像素坐标**：
     U[k] = 图集第 k 格的 x，V[k] = 第 k 格的 y
2. 图集 2048x2048 DXT3，格子 31x31；字形墨迹约 22x22，居中
3. 图集字形顺序 = charlist_CH[k + OFFSET]（本机原版 OFFSET = 5）

修复办法
--------
对每个乱码字 c（截图里看到它被显示成了 d）：
    源格 src = charlist.index(c) - OFFSET      # 这一格装着 c 的正确字形
    目标格 dst = charlist.index(d) - OFFSET     # 这一格是引擎实际取用、装着错字的格
把 src 格的 31x31 像素搬进 dst 格（只重编受影响的 DXT3 块）。

用法（命令行）
--------------
  # 1) 探测某字在候选格子里的位置，输出对照图（人工肉眼确认）
  python sr2font.py probe <vpp路径> <字> [span]

  # 2) 按 JSON 里的对照表生成修好的 vpp
  python sr2font.py fix <vpp路径> <pairs.json> <输出vpp路径> [OFFSET]

pairs.json 形如：
  {"offset": 5, "pairs": [["你", "使"], ["的", "發"], ...]}
"""
import os, re, struct, zlib, sys, json, hashlib

BW = 2048 // 4          # 每行 DXT3 块数
CELL = 31               # 格子边长
ATLAS_SIZE = 4194304    # 2048x2048 DXT3


# ----------------------------------------------------------------- VPP
class Vpp:
    def __init__(self, path, load_all=True):
        self.path = path
        self.load_all = load_all
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
        if load_all:
            self.f.seek(0)
            self.data = bytearray(self.f.read())

    def _z(self, p):
        e = self.meta.find(b"\x00", p)
        return self.meta[p:e].decode("ascii", "replace")

    def entries(self):
        r = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b_, c, d, ln = struct.unpack_from("<IIiii", self.meta, e)
            r.append(dict(idx=i, name=self._z(self.na + a),
                          ext=self._z(self.ea + b_) if b_ else "",
                          body=d, size=ln, entry_off=e))
        return r

    def find(self, name, ext=None):
        for e in self.entries():
            if e["name"].lower() == name.lower() and (ext is None or e["ext"].lower() == ext.lower()):
                return e
        return None

    def read(self, e):
        self.f.seek(self.ds + e["body"])
        return self.f.read(e["size"])

    def abs_offset(self, e):
        return self.ds + e["body"]


# ----------------------------------------------------------------- DXT3
def _rgb565(v):
    return (((v >> 11) & 0x1F) * 255 // 31, ((v >> 5) & 0x3F) * 255 // 63, (v & 0x1F) * 255 // 31)


def dec_block(buf, off):
    """DXT3(BC2) 块 -> 4x4 的 (r,g,b,a)"""
    b = buf[off:off + 16]
    c0 = b[8] | (b[9] << 8)
    c1 = b[10] | (b[11] << 8)
    idx = int.from_bytes(bytes(b[12:16]), "little")
    p0, p1 = _rgb565(c0), _rgb565(c1)
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
    """4x4 的 (r,g,b,a) -> DXT3 块（复刻本图集使用的「预乘灰度」编码）"""
    ab = bytearray(8)
    for py in range(4):
        for pxx in range(4):
            k = py * 4 + pxx
            ab[k // 2] |= max(0, min(15, px[py][pxx][3] >> 4)) << (4 * (k % 2))
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
            c = [abs(q - L), abs(q - t1), abs(q - t2)]
            pick = c.index(min(c))
            words |= ((0 if pick == 0 else (2 if pick == 1 else 3)) & 3) << (2 * k)
    o = bytearray(16)
    o[0:8] = ab
    o[8] = grey & 0xFF
    o[9] = (grey >> 8) & 0xFF
    o[12] = words & 0xFF
    o[13] = (words >> 8) & 0xFF
    o[14] = (words >> 16) & 0xFF
    o[15] = (words >> 24) & 0xFF
    return bytes(o)


def px_at(atlas, X, Y):
    return dec_block(atlas, ((Y // 4) * BW + X // 4) * 16)[Y % 4][X % 4]


# ----------------------------------------------------------------- 字体
class Font:
    """一个构建里的 图集 + vf3 + charlist"""

    def __init__(self, vpp_path, atlas_name="fnt_chinese", atlas_ext="g_peg_pc"):
        self.v = Vpp(vpp_path)
        self.atlas_entry = self.v.find(atlas_name, atlas_ext)
        if not self.atlas_entry:
            raise SystemExit("找不到图集 %s.%s" % (atlas_name, atlas_ext))
        self.atlas = self.v.read(self.atlas_entry)
        self.vf3_entry = self.v.find(atlas_name, "vf3_pc")
        self.vf3 = self.v.read(self.vf3_entry)
        self.cl_entry = self.v.find("charlist_CH", "txt")
        raw = self.v.read(self.cl_entry)
        m = re.search(rb"count\s*=\s*(\d+)", raw)
        body = raw[m.end():] if m else raw
        end = body.find(b"//ENDOFFILE")
        self.charlist = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
        N = struct.unpack_from("<I", self.vf3, 8)[0]
        self.N = N
        self.UOFF = 0xD0 + N * 16
        self.VOFF = self.UOFF + N * 4

    def uv(self, k):
        return (struct.unpack_from("<i", self.vf3, self.UOFF + k * 4)[0],
                struct.unpack_from("<i", self.vf3, self.VOFF + k * 4)[0])

    def idx(self, ch):
        cp = ord(ch)
        return self.charlist.index(cp) if cp in self.charlist else None

    def cell(self, atlas, k, pad=2, size=34):
        x, y = self.uv(k)
        x -= pad
        y -= pad
        return [[px_at(atlas, x + xx, y + yy) for xx in range(size)] for yy in range(size)]

    def probe_cells(self, ch, span=8):
        """返回 [(k, cell)]，k 从 idx(ch)-span 到 +span，用于肉眼找该字的真实格子"""
        i = self.idx(ch)
        return [(k, self.cell(self.atlas, k)) for k in range(i - span, i + span + 1)]

    def apply(self, pairs, offset):
        """pairs = [(原字, 被错误显示成的字)]；返回新图集 bytes"""
        out = bytearray(self.atlas)
        log = []
        for c, d in pairs:
            ic, idd = self.idx(c), self.idx(d)
            if ic is None or idd is None:
                raise SystemExit("字不在 charlist: %s / %s" % (c, d))
            s, t = ic - offset, idd - offset
            us, vs = self.uv(s)
            ut, vt = self.uv(t)
            src = [[px_at(self.atlas, us + xx, vs + yy) for xx in range(CELL)] for yy in range(CELL)]
            for by in range(vt // 4, (vt + CELL - 1) // 4 + 1):
                for bx in range(ut // 4, (ut + CELL - 1) // 4 + 1):
                    o = (by * BW + bx) * 16
                    blk = [list(r) for r in dec_block(self.atlas, o)]
                    for yy in range(4):
                        Y = by * 4 + yy
                        if not (vt <= Y < vt + CELL):
                            continue
                        for xx in range(4):
                            X = bx * 4 + xx
                            if ut <= X < ut + CELL:
                                blk[yy][xx] = src[Y - vt][X - ut]
                    out[o:o + 16] = enc_block(blk)
            log.append((c, d, s, t, (us, vs), (ut, vt)))
        return bytes(out), log

    def save_with_atlas(self, new_atlas, out_path):
        self.v.data[self.v.abs_offset(self.atlas_entry):
                    self.v.abs_offset(self.atlas_entry) + len(self.atlas)] = new_atlas
        open(out_path, "wb").write(bytes(self.v.data))


# ----------------------------------------------------------------- 调试用：输出 PNG
def png_gray(rows, scale, path):
    h, w = len(rows) * scale, len(rows[0]) * scale
    raw = bytearray()
    for r in rows:
        line = bytearray()
        for v in r:
            line += bytes([v]) * scale
        for _ in range(scale):
            raw += b"\x00" + bytes(line)

    def ck(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    o = b"\x89PNG\r\n\x1a\n" + ck(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
    o += ck(b"IDAT", zlib.compress(bytes(raw), 6)) + ck(b"IEND", b"")
    open(path, "wb").write(o)


def sheet(cells, path, scale=3, cols=12, gap=3):
    cw = len(cells[0][0]) * scale
    rowsn = (len(cells) + cols - 1) // cols
    cv = [[25] * (cols * (cw + gap)) for _ in range(rowsn * (cw + gap))]
    for n, c in enumerate(cells):
        px, py = (n % cols) * (cw + gap), (n // cols) * (cw + gap)
        for yy in range(cw):
            for xx in range(cw):
                cv[py + yy][px + xx] = c[yy // scale][xx // scale]
    png_gray(cv, 1, path)


# ----------------------------------------------------------------- CLI
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "probe":
        vpp, ch = sys.argv[2], sys.argv[3]
        span = int(sys.argv[4]) if len(sys.argv) > 4 else 8
        f = Font(vpp)
        i = f.idx(ch)
        print("charlist_CH = %d 项；%s 的索引 = %d" % (len(f.charlist), ch, i))
        cells = []
        ks = list(range(i - span, i + span + 1))
        for k in ks:
            cells.append([[p[3] for p in row] for row in f.cell(f.atlas, k)])
        out = r"F:/sr2-cn/_probe_%s.png" % ch
        sheet(cells, out)
        print("候选格子索引 %d..%d -> 已输出 %s（人工读出哪一格是「%s」）" % (ks[0], ks[-1], out, ch))
    elif cmd == "fix":
        vpp, pairfile, outp = sys.argv[2], sys.argv[3], sys.argv[4]
        cfg = json.load(open(pairfile, encoding="utf-8"))
        offset = int(cfg.get("offset", 5))
        f = Font(vpp)
        newat, log = f.apply([tuple(p) for p in cfg["pairs"]], offset)
        f.save_with_atlas(newat, outp)
        print("offset=%d，共 %d 处替换" % (offset, len(log)))
        for c, d, s, t, sv, tv in log:
            print("  %s(显示为 %s): 格 %-5d(%4d,%3d) -> 格 %-5d(%4d,%3d)" % (c, d, s, sv[0], sv[1], t, tv[0], tv[1]))
        print("输出: %s  md5=%s" % (outp, hashlib.md5(open(outp, "rb").read()).hexdigest()))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
