# -*- coding: utf-8 -*-
"""极简 VPP 读取（不依赖 numpy），用于内存搜索脚本。"""
import struct

MAGIC = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])


class MiniVpp:
    def __init__(self, path):
        self.data = open(path, 'rb').read()
        d = self.data
        assert d[:5] == MAGIC
        o = 5 + 0x14F
        self.num, self.csize, self.lo, self.lf, self.le = struct.unpack_from('<iiiii', d, o)
        self.names_at = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.lf) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.le) & 0xFFFFF800) + 0x800

    def _s(self, base, pos):
        e = self.data.find(b'\x00', base + pos)
        return self.data[base + pos:e].decode('ascii', 'replace')

    def entries(self):
        out = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b, c, dd, ln, m1, z = struct.unpack_from('<IIiiiii', self.data, e)
            out.append(dict(name=self._s(self.names_at, a),
                            ext=self._s(self.ext_at, b) if b else '',
                            body=dd, size=ln))
        return out

    def read(self, ent):
        p = self.data_start + ent['body']
        return self.data[p:p + ent['size']]

    def find(self, name, ext=None):
        for e in self.entries():
            if e['name'].lower() == name.lower() and (ext is None or e['ext'].lower() == ext.lower()):
                return e
        return None
