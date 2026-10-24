# -*- coding: utf-8 -*-
"""Decisive test: read le_strings static_CH records, compare subtitle vs HUD."""
import sys, struct, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])

class Vpp:
    def __init__(self, path):
        self.path = path
        self.data = bytearray(open(path, 'rb').read())
        d = self.data
        assert d[:5] == MAGIC_VPP, 'not an SR2 VPP'
        o = 5 + 0x14F
        (self.num, self.container_size, self.len_offsets,
         self.len_filenames, self.len_extensions) = struct.unpack_from('<iiiii', d, o)
        self.names_at = ((0x800 + self.len_offsets) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.len_filenames) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.len_extensions) & 0xFFFFF800) + 0x800
    def _strz(self, base, pos):
        e = self.data.find(b'\x00', base + pos)
        return self.data[base + pos:e].decode('ascii', 'replace')
    def entries(self):
        out = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b, c, d, ln, m1, z = struct.unpack_from('<IIiiiii', self.data, e)
            out.append(dict(idx=i, name=self._strz(self.names_at, a),
                            ext=self._strz(self.ext_at, b) if b else '',
                            body=d, size=ln, entry_off=e))
        return out
    def read(self, ent):
        p = self.data_start + ent['body']
        return bytes(self.data[p:p + ent['size']])
    def find(self, name, ext=None):
        for e in self.entries():
            if e['name'].lower() == name.lower() and (ext is None or e['ext'].lower() == ext.lower()):
                return e
        return None

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
ents = pv.entries()
print("patch entries:", len(ents))
stat = [e for e in ents if 'static' in e['name'].lower()]
for e in stat:
    print("  cand:", e['idx'], e['name'], e['ext'], e['size'])
