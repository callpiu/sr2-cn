# -*- coding: utf-8 -*-
# 交接前核查（不依赖 numpy）：松散文件、其它表是否含字幕文本、当前游戏包状态
import os, sys, re, struct, hashlib

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])


class Vpp:
    """最小 VPP 读取器（只读，等价于 sr2lib 的 Vpp.read/find/entries）。"""

    def __init__(self, path):
        self.d = open(path, "rb").read()
        assert self.d[:5] == MAGIC_VPP, "not a VPP: " + path
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
            if e["name"].lower() == name.lower() and (ext is None or e["ext"].lower() == ext.lower()):
                return e
        return None


def parse_le(data):
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


print("=== 1. 游戏根目录松散文件 / 可能的加载器 ===")
for f in sorted(os.listdir(G)):
    p = os.path.join(G, f)
    if os.path.isdir(p):
        try:
            n = len(os.listdir(p))
        except Exception:
            n = -1
        print("  [DIR ] %-26s (%d 项)" % (f, n))
    else:
        print("  [FILE] %-26s %12d B" % (f, os.path.getsize(p)))

print("\n=== 2. 四个包当前 md5 ===")
for f in ["patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc", "pegs.vpp_pc"]:
    print("  %-18s %s" % (f, hashlib.md5(open(os.path.join(G, f), "rb").read()).hexdigest()))

v = Vpp(os.path.join(G, "patch.vpp_pc"))
cl = [int(x) for x in re.findall(rb"\d+", v.read(v.find("charlist_CH", "txt")))]


def dec(slots):
    return "".join(chr(cl[w - 0x20]) if 0 <= w - 0x20 < len(cl) else "?" for w in slots)


KEY = "弟兄们"
print("\n=== 3. 含「%s」的记录分布 ===" % KEY)
for tab in ["static_CH", "voice_script_CH", "platform_pc_CH"]:
    e = v.find(tab, "le_strings")
    if not e:
        print("  %-18s 不存在" % tab)
        continue
    rows = parse_le(v.read(e))
    hits = [(i, h, dec(s)) for i, h, s in rows if KEY in dec(s)]
    print("  %-18s 共 %5d 条，含「%s」= %d 条" % (tab, len(rows), KEY, len(hits)))
    for i, h, t in hits[:8]:
        print("        idx=%-6d hA=%08X  %s" % (i, h, t[:72]))

print("\n=== 4. voice_script_CH 中含 homies/Homies 的条目（前6条） ===")
e = v.find("voice_script_CH", "le_strings")
rows = parse_le(v.read(e))
n = 0
for i, h, s in rows:
    t = dec(s)
    if "homie" in t.lower() or "弟兄" in t:
        print("        idx=%-6d hA=%08X  %s" % (i, h, t[:80]))
        n += 1
        if n >= 6:
            break
print("  （本段命中 %d 条）" % n)
