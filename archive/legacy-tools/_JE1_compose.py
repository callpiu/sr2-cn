# -*- coding: utf-8 -*-
# 组合验证：引擎输出的索引 是「哪张表 × 哪个索引」的组合
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


def load_cl(v, fname):
    e = v.find(fname, "txt")
    if not e:
        return None
    b = v.read(e)
    m = re.search(rb"count\s*=\s*(\d+)", b)
    body = b[m.end():] if m else b
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


v_off = Vpp(os.path.join(G, "patch.vpp_pc"))
OFF = load_cl(v_off, "charlist_CH")
v_cn = Vpp(r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2")
CN = load_cl(v_cn, "charlist_CH")
print("官方表 =", len(OFF), " 汉化表 =", len(CN))

TEXT = "你的兄弟們需要保護"
OBS = "使發光彈借雇複使發俱謗"  # 若图集是官方的，屏幕上应是这串（第三方读数）

print("\n字符  官方idx  汉化idx | OFF[汉化idx]  CN[官方idx]  观测显示")
print("-" * 72)
for k, c in enumerate(TEXT):
    o = OFF.index(ord(c)) if ord(c) in OFF else None
    n = CN.index(ord(c)) if ord(c) in CN else None
    a = chr(OFF[n]) if (n is not None and n < len(OFF)) else "-"
    b = chr(CN[o]) if (o is not None and o < len(CN)) else "-"
    print(" %s      %-7s  %-7s |   %-9s  %-9s   %s" % (c, o, n, a, b, OBS[k]))

print("\n=== 直接查关键位置 ===")
for i in [330, 331, 332, 333, 334, 335, 336, 337]:
    print("  idx %-4d 官方表=%s  汉化表=%s" % (i, chr(OFF[i]), chr(CN[i]) if i < len(CN) else "-"))
