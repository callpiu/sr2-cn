# -*- coding: utf-8 -*-
# 交接核查 4：定位当前构建里中文字幕文本的真实位置
import os, re, struct

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])


class Vpp:
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


v = Vpp(os.path.join(G, "patch.vpp_pc"))

print("=== 1. 当前 charlist_CH.txt 结构 ===")
clb = v.read(v.find("charlist_CH", "txt"))
head = clb[:300].decode("latin1", "replace")
print("  头部:", " | ".join(x for x in head.split("\r\n")[:6]))
m = re.search(rb"count\s*=\s*(\d+)", clb)
print("  count 头 =", m.group(1).decode() if m else "无")
body = clb[m.end():] if m else clb
end = body.find(b"//ENDOFFILE")
nums = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
print("  条目数 =", len(nums))
print("  前 12 项 =", nums[:12])
print("  后 8 项 =", nums[-8:])
print("  是否严格递增 =", all(nums[i] < nums[i + 1] for i in range(len(nums) - 1)))
cjk = [x for x in nums if 0x4E00 <= x <= 0x9FFF]
print("  CJK 项数 =", len(cjk), " 首个CJK =", hex(cjk[0]) if cjk else None)

print("\n=== 2. static_CH 用该 charlist 解码（尝试不同偏移） ===")
e = v.find("static_CH", "le_strings")
rows = parse_le(v.read(e))
print("  static_CH 记录数 =", len(rows))
rec = rows[0]
print("  首条 hA=%08X slots=%d" % (rec[1], len(rec[2])))
print("  槽位(前12) =", [hex(x) for x in rec[2][:12]])
for off in (0x20, 0x00, 0x1F, 0x21):
    t = "".join(chr(nums[w - off]) if 0 <= w - off < len(nums) else "?" for w in rec[2])
    print("  offset=0x%02X -> %s" % (off, t[:70]))

print("\n=== 3. 各表含 CJK 的记录数（用当前 charlist） ===")


def dec(slots, off=0x20):
    return "".join(chr(nums[w - off]) if 0 <= w - off < len(nums) else "?" for w in slots)


for tab in ["static_CH", "voice_script_CH", "platform_pc_CH"]:
    ee = v.find(tab, "le_strings")
    if not ee:
        continue
    rr = parse_le(v.read(ee))
    c = sum(1 for _, _, s in rr if any(0x4E00 <= ord(ch) <= 0x9FFF for ch in dec(s)))
    print("  %-18s %5d 条，含 CJK = %d" % (tab, len(rr), c))
    # 找几条含 CJK 的看看
    shown = 0
    for i, h, s in rr:
        t = dec(s)
        if any(0x4E00 <= ord(ch) <= 0x9FFF for ch in t):
            print("        idx=%-6d hA=%08X  %s" % (i, h, t[:70]))
            shown += 1
            if shown >= 4:
                break

print("\n=== 4. Mods/hud_msg.lua 里的字体设置 ===")
p = os.path.join(G, "Mods", "hud_msg.lua")
if os.path.exists(p):
    txt = open(p, "r", errors="replace").read()
    for i, ln in enumerate(txt.split("\n"), 1):
        if "font" in ln.lower():
            print("  %5d| %s" % (i, ln.rstrip()[:130]))
else:
    print("  不存在")

print("\n=== 5. patch 内 hud_msg.lua 的字体设置（对比） ===")
he = v.find("hud_msg", "lua")
if he:
    txt = v.read(he).decode("latin1")
    for i, ln in enumerate(txt.split("\n"), 1):
        if "font" in ln.lower():
            print("  %5d| %s" % (i, ln.rstrip()[:130]))
else:
    print("  不存在")

print("\n=== 6. debug.txt 里 hud_msg / static_CH 相关加载记录 ===")
t = open(os.path.join(G, "debug.txt"), "r", errors="replace").read()
for kw in ["hud_msg", "static_CH", "voice_script_CH", "charlist_CH"]:
    hits = [ln for ln in t.split("\n") if kw.lower() in ln.lower()]
    print("  %-18s 命中 %d 行" % (kw, len(hits)))
    for ln in hits[:5]:
        print("      ", ln.strip()[:150])
