# -*- coding: utf-8 -*-
# 核验对方文档 §4.5 的 vf3 结构断言（V 表是否真的少 5 项）
import os, struct

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])


class Vpp:
    def __init__(self, path):
        self.d = open(path, "rb").read()
        o = 5 + 0x14F
        self.num = struct.unpack_from("<i", self.d, o)[0]
        self.len_offsets = struct.unpack_from("<i", self.d, o + 8)[0]
        self.len_filenames = struct.unpack_from("<i", self.d, o + 12)[0]
        self.len_extensions = struct.unpack_from("<i", self.d, o + 16)[0]
        self.names_at = ((0x800 + self.len_offsets) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.len_filenames) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.len_extensions) & 0xFFFFF800) + 0x800

    def _strz(self, base, pos):
        e = self.d.find(b"\x00", base + pos)
        return self.d[base + pos:e].decode("ascii", "replace")

    def entries(self):
        out = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b, c, d, ln = struct.unpack_from("<IIiii", self.d, e)
            out.append(dict(name=self._strz(self.names_at, a),
                            ext=self._strz(self.ext_at, b) if b else "",
                            body=d, size=ln))
        return out

    def read(self, ent):
        p = self.data_start + ent["body"]
        return self.d[p:p + ent["size"]]

    def find(self, name, ext=None):
        for e in self.entries():
            if e["name"].lower() == name.lower() and (ext is None or e["ext"].lower() == ext.lower()):
                return e
        return None


for pkg in ["common.vpp_pc", "patch.vpp_pc"]:
    v = Vpp(os.path.join(G, pkg))
    e = v.find("fnt_chinese", "vf3_pc")
    if not e:
        print("[%s] 无 fnt_chinese.vf3_pc" % pkg)
        continue
    b = v.read(e)
    n = len(b)
    print("=" * 66)
    print("[%s] fnt_chinese.vf3_pc = %d B (%#x)" % (pkg, n, n))
    print("  magic =", b[:4])
    ver = struct.unpack_from("<I", b, 4)[0]
    N = struct.unpack_from("<I", b, 8)[0]
    print("  ver = %d   N = %d" % (ver, N))
    print("  头部前 64 字节:", " ".join("%02X" % x for x in b[:64]))
    # 头部文本（PegName / Bitmap）
    for kw in (b".peg", b".tga", b"fnt_"):
        i = b.find(kw)
        if i >= 0:
            s = i
            while s > 0 and 32 <= b[s - 1] < 127:
                s -= 1
            t = i
            while t < len(b) and 32 <= b[t] < 127:
                t += 1
            print("  字符串 @%#x: %r" % (s, b[s:t].decode("latin1")))
    # 记录区：0xD0 起 N*16
    rec_end = 0xD0 + N * 16
    print("  记录区 0xD0..%#x (%d 条 × 16 = %d B)" % (rec_end, N, N * 16))
    u_off = rec_end
    u_end = u_off + N * 4
    v_off = u_end
    v_end = v_off + N * 4
    print("  U 表 %#x..%#x  (%d 项)  需 %#x" % (u_off, u_end, N, u_end))
    print("  V 表 %#x..%#x  (%d 项)  需 %#x" % (v_off, v_end, N, v_end))
    print("  文件末 %#x" % n)
    if v_end > n:
        miss = (v_end - n) // 4
        print("  >>> V 表被截断: 缺 %d 项 (%d 字节)" % (miss, v_end - n))
    else:
        print("  >>> 表完整")
    # 抽查对方给的三组 UV：槽位-0x20 = 405/962/358
    for idx, want in ((405, "兄"), (962, "弟"), (358, "們")):
        if u_off + idx * 4 + 4 <= n:
            u = struct.unpack_from("<i", b, u_off + idx * 4)[0]
            if v_off + idx * 4 + 4 <= n:
                vv = struct.unpack_from("<i", b, v_off + idx * 4)[0]
            else:
                vv = None
            print("  索引 %-5d (期望 %s): U=%-6s V=%-6s" % (idx, want, u, vv))
        else:
            print("  索引 %-5d: 超出文件" % idx)
