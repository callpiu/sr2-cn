# -*- coding: utf-8 -*-
# 用 22 组对照反推引擎表 M 的内容：M[B.index(显示字)] == 原字
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
print("OFF=%d  B(汉化)=%d\n" % (len(OFF), len(B)))

EXP1 = "你的兄弟們需要你的保護"
DIS1 = "任璨偶巧位雄衡任璨伪该"
EXP2 = "你的兄弟們正要去進行交易保護他們避免受到攻擊"
DIS2 = "任璨偶巧位校衡勾远貌乱携伪该亡位通像匪冰挺拮"
assert len(EXP1) == len(DIS1), (len(EXP1), len(DIS1))
assert len(EXP2) == len(DIS2), (len(EXP2), len(DIS2))

pairs = {}
for a, b in [(EXP1, DIS1), (EXP2, DIS2)]:
    for x, y in zip(a, b):
        pairs.setdefault(x, y)

print("原字  码点     M索引(=B中显示字位置)  M索引处OFF的值      M索引处B的值")
print("-" * 76)
rows = []
for x, y in pairs.items():
    j = B.index(ord(y))
    rows.append((j, x, y))
rows.sort()
for j, x, y in rows:
    o = OFF[j] if j < len(OFF) else None
    bb = B[j] if j < len(B) else None
    print(" %s  U+%04X   %-6d  %-6s(U+%04X)   %s" % (
        x, ord(x), j,
        chr(o) if o else "-", o if o else 0,
        chr(bb) if bb else "-"))

print("\n=== 检查：M 索引 j 处，B[j] 是否等于显示字（必然），OFF[j] 是什么 ===")
same_as_off = sum(1 for j, x, y in rows if j < len(OFF) and OFF[j] == ord(x))
print("在 %d 个点中，OFF[j] == 原字 的个数 = %d" % (len(rows), same_as_off))

# 单调性 & 局部密度对比
print("\n=== 局部密度（相邻原字之间 M 的格数 vs OFF 的格数）===")
for i in range(len(rows) - 1):
    j1, x1, _ = rows[i]
    j2, x2, _ = rows[i + 1]
    o1 = OFF.index(ord(x1)) if ord(x1) in OFF else None
    o2 = OFF.index(ord(x2)) if ord(x2) in OFF else None
    print("  %s(U+%04X) -> %s(U+%04X) : M格数=%-4d OFF格数=%s" % (
        x1, ord(x1), x2, ord(x2), j2 - j1, (o2 - o1) if (o1 is not None and o2 is not None) else "?"))
