# -*- coding: utf-8 -*-
# 检查 vf3 字体文件内部是否自带「字形索引 -> Unicode 码点」表
# 若是，且与 charlist_CH.txt 不一致 => 就是乱码根源
import os, re, struct

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"


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


CHARS = "你的兄弟們需要保護"
IDX_ENGINE = [336, 1784, 410, 967, 362, 2656, 2268, 354, 2342]  # 引擎实际输出的索引
IDX_TRUE_OFF = [333, 1787, 405, 962, 358, 2672, 2279, 350, 2353]  # 官方表里的正确索引

for src, tag in [(os.path.join(G, "patch.vpp_pc"), "patch"),
                 (os.path.join(G, "common.vpp_pc"), "common")]:
    if not os.path.exists(src):
        continue
    v = Vpp(src)
    print("#" * 72)
    print("### %s.vpp_pc" % tag)
    for fn in ["fnt_chinese", "fnt_body_n", "fnt_body_s"]:
        e = v.find(fn, "vf3_pc")
        if not e:
            print("  %s.vf3_pc : 不存在" % fn)
            continue
        b = v.read(e)
        print("\n  --- %s.vf3_pc  size=%d (0x%X) ---" % (fn, len(b), len(b)))
        # 头部
        print("   头 0x00-0x1F:", b[:0x20].hex(" "))
        # 找 N：试几种偏移
        for off in (0x04, 0x08, 0x0C, 0x10, 0xB0, 0xB4, 0xB8, 0xBC, 0xC0, 0xC4, 0xC8, 0xCC):
            if off + 4 <= len(b):
                val = struct.unpack_from("<I", b, off)[0]
                if 100 < val < 20000:
                    print("   [<I] @0x%02X = %d" % (off, val))
        # 搜索码点
        print("   码点搜索（u16 LE / BE）:")
        for c in CHARS:
            cp = ord(c)
            le = struct.pack("<H", cp)
            be = struct.pack(">H", cp)
            poss_le = []
            st = 0
            while True:
                p = b.find(le, st)
                if p < 0:
                    break
                poss_le.append(p)
                st = p + 1
                if len(poss_le) > 12:
                    break
            poss_be = []
            st = 0
            while True:
                p = b.find(be, st)
                if p < 0:
                    break
                poss_be.append(p)
                st = p + 1
                if len(poss_be) > 12:
                    break
            print("     %s U+%04X  LE@%s  BE@%s" % (c, cp, poss_le[:12], poss_be[:12]))
