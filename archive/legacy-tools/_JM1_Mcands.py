# -*- coding: utf-8 -*-
# 测试各种候选 M 表
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

TARGET = {}
for a, b in [("交", "乱"), ("他", "亡"), ("你", "任"), ("保", "伪"), ("們", "位"),
             ("兄", "偶"), ("免", "像"), ("到", "冰"), ("去", "勾"), ("受", "匪"),
             ("弟", "巧"), ("擊", "拮"), ("攻", "挺"), ("易", "携"), ("正", "校"),
             ("的", "璨"), ("要", "衡"), ("護", "该"), ("行", "貌"), ("進", "远"),
             ("避", "通"), ("需", "雄")]:
    TARGET[ord(a)] = B.index(ord(b))

SO, SB = set(OFF), set(B)
cands = {
    "OFF": OFF,
    "B": B,
    "sorted(OFF∪B)": sorted(SO | SB),
    "sorted(OFF∩B)": sorted(SO & SB),
    "sorted(OFF-B)": sorted(SO - SB),
    "sorted(B-OFF)": sorted(SB - SO),
    "sorted(OFF ∪ ASCII0-31)": sorted(SO | set(range(0, 32))),
    "sorted(OFF ∪ B ∪ ASCII0-31)": sorted(SO | SB | set(range(0, 32))),
    "sorted(OFF + 0x00-0x1F)": sorted(SO | set(range(0, 32))),
}
# 另一个思路：M = OFF 但把 [0,31] 也算进去
for tag, arr in cands.items():
    hit = 0
    det = []
    for cp, want in TARGET.items():
        try:
            got = arr.index(cp)
        except ValueError:
            got = None
        if got == want:
            hit += 1
        if len(det) < 6:
            det.append("%s:%s/%s" % (chr(cp), got, want))
    print("%-32s len=%-6d 命中=%2d/22  %s" % (tag, len(arr), hit, " ".join(det)))

print("\n=== 差值的分布（OFF 索引 - 目标）===")
for cp, want in sorted(TARGET.items()):
    o = OFF.index(cp)
    b = B.index(cp) if cp in SB else None
    print("  %s U+%04X  OFF=%-5d B=%-5s 目标=%-5d  (目标-OFF=%+d)" % (
        chr(cp), cp, o, b, want, want - o))
