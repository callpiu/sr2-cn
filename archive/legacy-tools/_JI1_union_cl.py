# -*- coding: utf-8 -*-
# 检验：引擎的表 T 是否为「多张 charlist 的并集（按 Unicode 排序）」
import os, re, struct, itertools

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
            if e["name"].lower() == name.lower() and (ext is None or e["ext"].lower() == ext.lower()):
                return e
        return None


def load_cl(v, fname):
    e = v.find(fname, "txt")
    if not e:
        return None
    b = v.read(e)
    m = re.search(rb"count\s*=\s*(\d+)", b)
    body = b[m.end():] if m else b
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


WANT = {}
for c, i in zip("你的兄弟們需要保護", [336, 1784, 410, 967, 362, 2656, 2268, 354, 2342]):
    WANT[ord(c)] = i
TARGET_CHARS = [ord(c) for c in "你的兄弟們需要保護"]

tables = {}
for fn in ["patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc", "pegs.vpp_pc"]:
    p = os.path.join(G, fn)
    if not os.path.exists(p):
        continue
    v = Vpp(p)
    for e in v.entries():
        if e["ext"].lower() != "txt":
            continue
        if "charlist" not in e["name"].lower():
            continue
        cl = load_cl(v, e["name"])
        if cl:
            tables["%s/%s" % (fn, e["name"])] = cl

print("可用表:", {k: len(v) for k, v in tables.items()})


def check(tag, arr):
    arr = sorted(set(arr))
    idx = {}
    for cp in WANT:
        idx[cp] = arr.index(cp) if cp in arr else None
    got = {cp: idx[cp] for cp in WANT}
    ok = got == WANT
    rev = {}
    for cp, i in WANT.items():
        if i < len(arr):
            rev[cp] = chr(arr[i])
    print("\n[%s] 长度=%d  匹配=%s" % (tag, len(arr), ok))
    if not ok:
        print("   目标:", {chr(k): v for k, v in WANT.items()})
        print("   实际:", {chr(k): v for k, v in got.items()})
        print("   反查 arr[目标idx] =", {chr(k): v for k, v in rev.items()})


names = list(tables.keys())
# 单表
for n in names:
    check(n, tables[n])
# 全并集
allc = []
for n in names:
    allc += tables[n]
check("全部并集", allc)
# CH + JP
ch = [k for k in names if "charlist_CH" in k][0]
jp = [k for k in names if "charlist_JP" in k][0]
check("CH ∪ JP", tables[ch] + tables[jp])
# 两两并集
for a, b in itertools.combinations(names, 2):
    check("∪ ".join([a.split("/")[1], b.split("/")[1]]), tables[a] + tables[b])
