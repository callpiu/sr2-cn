# -*- coding: utf-8 -*-
# 关键：目标记录到底在哪个 le_strings 里？static_CH / voice_script_CH / platform_pc_CH 全查
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
            out.append(dict(idx=i, name=self._strz(self.names_at, a),
                            ext=self._strz(self.ext_at, b) if b else "",
                            body=d, size=ln))
        return out

    def read(self, ent):
        p = self.data_start + ent["body"]
        return self.d[p:p + ent["size"]]

    def find(self, name, ext=None):
        for e in self.entries():
            if e["name"] == name and (ext is None or e["ext"].lower() == ext.lower()):
                return e
        return None


def records(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    po = 12 + buckets * 8
    out = []
    for idx in range(count):
        p = struct.unpack_from("<I", data, po + idx * 4)[0]
        if p + 4 > len(data):
            continue
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4
        slots = []
        while q + 2 <= len(data):
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0:
                break
            slots.append(w)
            q += 2
        out.append((idx, (id1 << 16) | id2, slots, p))
    return out


v = Vpp(os.path.join(G, "patch.vpp_pc"))
e = v.find("charlist_CH", "txt")
b = v.read(e)
m = re.search(rb"count\s*=\s*(\d+)", b)
body = b[m.end():] if m else b
end = body.find(b"//ENDOFFILE")
CL = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
print("charlist_CH =", len(CL), "项\n")


def decode(slots):
    return "".join(chr(CL[w - 0x20]) if 0 <= w - 0x20 < len(CL) else "?" for w in slots)


TARGETS = [0x84F287ED, 0x10AF1E62, 0xEC2D9F07, 0x95A79EDC, 0x343FEA1F, 0xE52F931A]

for fname in ["static_CH", "voice_script_CH", "platform_pc_CH"]:
    ent = v.find(fname, "le_strings")
    if not ent:
        print("### %s : 不存在" % fname)
        continue
    data = v.read(ent)
    rows = records(data)
    byid = {h: (i, s) for i, h, s, p in rows}
    print("### %s  size=%d  记录数=%d" % (fname, len(data), len(rows)))
    for h in TARGETS:
        if h in byid:
            i, s = byid[h]
            print("   命中 %08X  idx=%d slots=%d  文本: %s" % (h, i, len(s), decode(s)))
    # 额外：找含「兄弟」或「保護」的记录
    hits = 0
    for i, h, s, p in rows:
        t = decode(s)
        if "兄弟" in t or "保護" in t or "保护" in t:
            print("   [关键词] %08X idx=%d : %s" % (h, i, t[:70]))
            hits += 1
            if hits > 12:
                break
    print()

print("=== 六个目标 hash 在哪些文件出现 ===")
for fname in ["static_CH", "voice_script_CH", "platform_pc_CH"]:
    ent = v.find(fname, "le_strings")
    if not ent:
        continue
    rows = records(v.read(ent))
    ids = {h for _, h, _, _ in rows}
    print("  %-18s 含目标: %s" % (fname, [hex(h) for h in TARGETS if h in ids]))
