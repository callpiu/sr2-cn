# -*- coding: utf-8 -*-
# 列出所有 le_strings 条目的【精确名称】（大小写敏感），并列出游戏目录松散文件
import os, struct, glob

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


for fn in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    v = Vpp(fn)
    ls = [e for e in v.entries() if e["ext"].lower() == "le_strings"]
    if not ls:
        continue
    print("### %s  (%d 个 le_strings)" % (os.path.basename(fn), len(ls)))
    for e in ls:
        print("   [%4d] %-28s size=%d" % (e["idx"], e["name"], e["size"]))
    print()

print("=" * 70)
print("游戏目录根下的非 vpp 文件（松散文件检查）:")
for p in sorted(glob.glob(os.path.join(G, "*"))):
    if os.path.isdir(p):
        print("   [DIR ]", os.path.basename(p))
    elif not p.lower().endswith(".vpp_pc"):
        print("   [FILE] %-40s %d" % (os.path.basename(p), os.path.getsize(p)))
