# -*- coding: utf-8 -*-
# 核对官方记录 0x84F287ED / 0x10AF1E62 的真实内容，与对方文档比对
import os, re, struct

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


def records(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    po = 12 + buckets * 8
    out = []
    for idx in range(count):
        p = struct.unpack_from("<I", data, po + idx * 4)[0]
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4
        slots = []
        while q + 2 <= len(data):
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0:
                break
            slots.append(w)
            q += 2
        out.append((idx, (id1 << 16) | id2, slots))
    return out


v = Vpp(os.path.join(G, "patch.vpp_pc"))
cb = v.read(v.find("charlist_CH", "txt"))
m = re.search(rb"count\s*=\s*(\d+)", cb)
body = cb[m.end():] if m else cb
end = body.find(b"//ENDOFFILE")
CL = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
print("官方 charlist =", len(CL), "项")

rows = records(v.read(v.find("static_CH", "le_strings")))
byid = {h: (i, s) for i, h, s in rows}

TARGETS = [0x84F287ED, 0x10AF1E62, 0xEC2D9F07]
FIXED = [336, 1784, 410, 967, 362, 2656, 2268, 336, 1784, 354, 2342]

for h in TARGETS:
    if h not in byid:
        print("\n%08X: 不在官方 static_CH" % h)
        continue
    i, s = byid[h]
    t = "".join(chr(CL[w - 0x20]) if 0 <= w - 0x20 < len(CL) else "?" for w in s)
    print("\n%08X idx=%d slots=%d" % (h, i, len(s)))
    print("  槽位:", s)
    print("  解码:", t)

print("\n=== 关键比对：把官方记录槽位-0x20 与固定索引序列对照 ===")
h = 0x84F287ED
i, s = byid[h]
idx_actual = [w - 0x20 for w in s]
print("  官方记录 槽位-0x20 =", idx_actual)
print("  固定索引序列      =", FIXED)
print("  是否相同 =", idx_actual == FIXED)

# 官方记录里可见字符（去掉 [ ] 标签）的槽位
print("\n=== 官方记录里的可见字符与显示对照 ===")
vis = [(k, w) for k, w in enumerate(s) if 0x20 <= w - 0x20 < len(CL)]
for k, w in vis:
    c = chr(CL[w - 0x20])
    if c in "[]" or c.isascii():
        continue
    print("    位置%-3d 槽位%-6d 索引%-6d 字符=%s" % (k, w, w - 0x20, c))
