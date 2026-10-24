# -*- coding: utf-8 -*-
# 决定性：用 22 组已知 (字符 -> 引擎索引) 反推引擎的「查表算法」
# 关键事实：显示字 伪/该 只在汉化表 B 里，不在官方表 OFF 里 => 图集顺序 = B
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
            if e["name"].lower() == name.lower() and (ext is None or e["ext"].lower() == ext.lower()):
                return e
        return None


def load_cl(v, fname):
    b = v.read(v.find(fname, "txt"))
    m = re.search(rb"count\s*=\s*(\d+)", b)
    body = b[m.end():] if m else b
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


OFF = load_cl(Vpp(os.path.join(G, "patch.vpp_pc")), "charlist_CH")
B = load_cl(Vpp(r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2"), "charlist_CH")

# 22 组：(原字, 显示字)
PAIRS = [
    ("交", "乱"), ("他", "亡"), ("你", "任"), ("保", "伪"), ("們", "位"),
    ("兄", "偶"), ("免", "像"), ("到", "冰"), ("去", "勾"), ("受", "匪"),
    ("弟", "巧"), ("擊", "拮"), ("攻", "挺"), ("易", "携"), ("正", "校"),
    ("的", "璨"), ("要", "衡"), ("護", "该"), ("行", "貌"), ("進", "远"),
    ("避", "通"), ("需", "雄"),
]

TARGET = {}   # 原字 -> 引擎索引
for a, b in PAIRS:
    TARGET[ord(a)] = B.index(ord(b))

print("目标（引擎索引 = 显示字在汉化表 B 中的位置）:")
print({chr(k): v for k, v in TARGET.items()})
print()


def s16(x):
    return x - 0x10000 if x >= 0x8000 else x


def bsearch(arr, key, signed=False, lower=False):
    lo, hi = 0, len(arr) - 1
    k = s16(key) if signed else key
    res = None
    while lo <= hi:
        mid = (lo + hi) // 2
        v = s16(arr[mid]) if signed else arr[mid]
        if v == k:
            if not lower:
                return mid
            res = mid
            hi = mid - 1
            continue
        if v < k:
            lo = mid + 1
        else:
            hi = mid - 1
    return res if lower else None


models = {}
for tname, T in [("OFF", OFF), ("B", B)]:
    models["%s:直接index" % tname] = (lambda T: (lambda c: T.index(c)))(T)
    models["%s:无符号bsearch" % tname] = (lambda T: (lambda c: bsearch(T, c, False, False)))(T)
    models["%s:无符号lower" % tname] = (lambda T: (lambda c: bsearch(T, c, False, True)))(T)
    models["%s:有符号bsearch" % tname] = (lambda T: (lambda c: bsearch(T, c, True, False)))(T)
    models["%s:有符号lower" % tname] = (lambda T: (lambda c: bsearch(T, c, True, True)))(T)

print("%-20s %s" % ("模型", "命中/22   明细(前8个)"))
print("-" * 78)
for mname, fn in models.items():
    hit = 0
    detail = []
    for cp, want in TARGET.items():
        try:
            got = fn(cp)
        except Exception:
            got = None
        if got == want:
            hit += 1
        if len(detail) < 8:
            detail.append("%s:%s/%s" % (chr(cp), got, want))
    print("%-20s %-9s %s" % (mname, "%d/22" % hit, " ".join(detail)))
