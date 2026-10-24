# -*- coding: utf-8 -*-
# 交接核查 2：当前游戏环境真实状态（不依赖 numpy）
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


print("=== 1. Mods/ 目录内容（松散文件覆盖层） ===")
mods = os.path.join(G, "Mods")
if os.path.isdir(mods):
    for f in sorted(os.listdir(mods)):
        p = os.path.join(mods, f)
        if os.path.isdir(p):
            try:
                n = len(os.listdir(p))
            except Exception:
                n = -1
            print("  [DIR ] %-40s (%d 项)" % (f, n))
        else:
            print("  [FILE] %-40s %10d B" % (f, os.path.getsize(p)))
else:
    print("  无 Mods 目录")

print("\n=== 2. loose.txt / README.txt / FILELIST.txt ===")
for fn in ["loose.txt", "README.txt", "FILELIST.txt", "juiced.ini"]:
    p = os.path.join(G, fn)
    if os.path.exists(p):
        print("--- %s ---" % fn)
        t = open(p, "r", errors="replace").read()
        print("\n".join(t.split("\n")[:40]))
        print()

print("=== 3. debug.txt 中 LOOSE_FILE 统计 ===")
p = os.path.join(G, "debug.txt")
if os.path.exists(p):
    t = open(p, "r", errors="replace").read()
    lf = re.findall(r"\[LOOSE_FILE\]\s*(\S+)", t)
    print("  [LOOSE_FILE] 条目数 =", len(lf))
    print("  其中 lua =", sum(1 for x in lf if x.lower().endswith(".lua")))
    print("  其中 le_strings =", [x for x in lf if "le_strings" in x.lower()][:10])
    print("  其中 charlist/vf3/peg/txt =", [x for x in lf if any(k in x.lower() for k in ("charlist", "vf3", "peg", ".txt"))][:10])
    print("  前 25 条:", lf[:25])
else:
    print("  无 debug.txt")

print("\n=== 4. 当前 patch.vpp_pc 的 static_CH 概览 ===")
v = Vpp(os.path.join(G, "patch.vpp_pc"))
e = v.find("static_CH", "le_strings")
d = v.read(e)
magic, ver, buckets, count = struct.unpack_from("<I H H I", d, 0)
print("  static_CH: %d B  magic=%#x ver=%d buckets=%d count=%d" % (len(d), magic, ver, buckets, count))
ce = v.find("charlist_CH", "txt")
if ce:
    clb = v.read(ce)
    nums = [int(x) for x in re.findall(rb"\d+", clb)]
    has_count = re.search(rb"count\s*=\s*(\d+)", clb) is not None
    print("  charlist_CH.txt: %d B  数值项=%d  有 count 头=%s" % (len(clb), len(nums), has_count))
else:
    print("  charlist_CH.txt: 不存在")

# static_CH 前几条记录解码（用 patch 内 charlist）
if ce:
    cl = [int(x) for x in re.findall(rb"\d+", clb)]
    po = 12 + buckets * 8
    print("\n  static_CH 前 8 条记录（用 patch 内 charlist_CH 解码）:")
    for idx in range(8):
        p = struct.unpack_from("<I", d, po + idx * 4)[0]
        id1, id2 = struct.unpack_from("<HH", d, p)
        q = p + 4
        slots = []
        while q + 2 <= len(d):
            w = struct.unpack_from(">H", d, q)[0]
            if w == 0:
                break
            slots.append(w)
            q += 2
        t = "".join(chr(cl[w - 0x20]) if 0 <= w - 0x20 < len(cl) else "?" for w in slots)
        print("    idx=%-5d hA=%08X slots=%-4d %s" % (idx, (id1 << 16) | id2, len(slots), t[:80]))

print("\n=== 5. patch 内 le_strings 清单 ===")
ls = [x for x in v.entries() if x["ext"].lower() == "le_strings"]
print("  共", len(ls), "条")
for x in ls:
    print("    %-28s %10d B" % (x["name"] + "." + x["ext"], x["size"]))

print("\n=== 6. patch 内字体相关资源 ===")
for x in v.entries():
    if any(k in x["name"].lower() for k in ("fnt_", "charlist", "char_list")):
        print("    %-28s %-12s %10d B" % (x["name"], x["ext"] or "-", x["size"]))

print("\n=== 7. common / textures / pegs 里的字体资源 ===")
for fn in ["common.vpp_pc", "textures.vpp_pc", "pegs.vpp_pc"]:
    vv = Vpp(os.path.join(G, fn))
    got = [x for x in vv.entries() if any(k in x["name"].lower() for k in ("fnt_", "charlist", "vint_proj"))]
    print("  %-16s 共 %d 条目，字体相关 %d 个:" % (fn, vv.num, len(got)))
    for x in got[:30]:
        print("      %-30s %-12s %10d B" % (x["name"], x["ext"] or "-", x["size"]))
