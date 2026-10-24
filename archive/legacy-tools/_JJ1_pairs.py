# -*- coding: utf-8 -*-
# 用两张截图的 22 组 (原字 -> 显示字) 对照，反推引擎的字符表 T
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


v = Vpp(os.path.join(G, "patch.vpp_pc"))
OFF = load_cl(v, "charlist_CH")

# 两组样本（逗号被丢弃，已对齐）
EXP1 = "你的兄弟們需要保護"
DIS1 = "任璨偶巧位雄衡任璨伪该"
EXP2 = "你的兄弟們正要去進行交易保護他們避免受到攻擊"
DIS2 = "任璨偶巧位校衡勾远貌乱携伪该亡位通像匪冰挺拮"
print("对齐检查 sample1:", len(EXP1), len(DIS1))
print("对齐检查 sample2:", len(EXP2), len(DIS2))

pairs = {}
for a, b in [(EXP1, DIS1), (EXP2, DIS2)]:
    for x, y in zip(a, b):
        if x in pairs and pairs[x] != y:
            print("!! 冲突 %s -> %s / %s" % (x, pairs[x], y))
        pairs[x] = y

print("\n共 %d 组映射:" % len(pairs))
print("\n原字  码点   官方idx | 显示字 官方idx(引擎输出)  差值")
print("-" * 68)
rows = []
for x, y in pairs.items():
    ox = OFF.index(ord(x))
    oy = OFF.index(ord(y))
    rows.append((ord(x), x, ox, y, oy))
    print(" %s  U+%04X  %-6d |  %s   %-6d            %+d" % (x, ord(x), ox, y, oy, oy - ox))

print("\n按码点排序:")
for cp, x, ox, y, oy in sorted(rows):
    print("  U+%04X %s  offidx=%-5d -> %s offidx=%-5d  d=%+d" % (cp, x, ox, y, oy, oy - ox))

# 单调性检查
srt = sorted(rows)
mono = all(srt[i][4] <= srt[i + 1][4] for i in range(len(srt) - 1))
print("\n引擎输出索引对码点是否单调递增:", mono)
