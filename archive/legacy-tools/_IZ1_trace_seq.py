# -*- coding: utf-8 -*-
# 查这串固定索引 [336,1784,410,967,362,2656,2268,336,1784,354,2342] 的来源
import os, re, struct

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])
SEQ = [336, 1784, 410, 967, 362, 2656, 2268, 336, 1784, 354, 2342]
SLOTS = [x + 0x20 for x in SEQ]


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
cl = None
cb = v.read(v.find("charlist_CH", "txt"))
m = re.search(rb"count\s*=\s*(\d+)", cb)
body = cb[m.end():] if m else cb
end = body.find(b"//ENDOFFILE")
cl = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]

print("=== 目标槽位序列 ===")
print("  slots =", SLOTS)
print("  官方表解码 =", "".join(chr(cl[w - 0x20]) if 0 <= w - 0x20 < len(cl) else "?" for w in SLOTS))

print("\n=== 在 patch.vpp_pc 全部 le_strings 中搜索该序列 ===")
found_any = False
for e in v.entries():
    if e["ext"].lower() != "le_strings":
        continue
    nm = e["name"] + "." + e["ext"]
    try:
        rows = records(v.read(e))
    except Exception:
        continue
    for idx, h, slots in rows:
        if slots == SLOTS:
            print("  ★ 完全命中: %s idx=%d hA=%08X" % (nm, idx, h))
            found_any = True
        elif len(slots) == len(SLOTS) and slots[:5] == SLOTS[:5]:
            print("  近似命中: %s idx=%d hA=%08X slots=%s" % (nm, idx, h, slots[:12]))
if not found_any:
    print("  （无完全命中）")

print("\n=== 目标索引作为槽位，是否在别处出现 ===")
target_slots = set(SLOTS)
for e in v.entries():
    if e["ext"].lower() != "le_strings":
        continue
    nm = e["name"] + "." + e["ext"]
    try:
        rows = records(v.read(e))
    except Exception:
        continue
    for idx, h, slots in rows:
        inter = len(target_slots & set(slots))
        if inter >= 6:
            print("  %-26s idx=%-6d hA=%08X 交集=%d/%d" % (nm, idx, h, inter, len(SLOTS)))

print("\n=== 检查 voice_script_CH / platform_pc_CH / DLC 里的对应记录 ===")
for tab in ["voice_script_CH", "platform_pc_CH"]:
    e = v.find(tab, "le_strings")
    if not e:
        continue
    rows = records(v.read(e))
    print("  %s: %d 条" % (tab, len(rows)))

# 用索引序列反查：哪个 charlist 的「相邻关系」能解释 336,1784,410...
print("\n=== 索引序列本身的差值 ===")
for i in range(1, len(SEQ)):
    print("  %d→%d : %+d" % (SEQ[i - 1], SEQ[i], SEQ[i] - SEQ[i - 1]))
