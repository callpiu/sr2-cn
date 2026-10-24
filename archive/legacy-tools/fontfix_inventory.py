"""盘点 common / textures / pegs 里的字体资源。

用轻量流式读取（不整文件载入内存），因为 textures.vpp_pc 有 1.26 GB。

VPP 格式（来自交接文档 §5.3，已用 sr2lib 核对）：
    magic 5B = CE 0A 89 51 04
    @5+0x14F: num i32, container_size i32, len_offsets i32,
              len_filenames i32, len_extensions i32
    条目表 @0x800，28B/条:
      +0  name_off u32 (相对 names 区)
      +4  ext_off  u32 (0 = 无扩展名)
      +8  ?
      +12 body_off i32 (相对 data_start)
      +16 size     i32
    names_at   = ((0x800 + len_offsets) & 0xFFFFF800) + 0x800
    ext_at     = ((names_at + len_filenames) & 0xFFFFF800) + 0x800
    data_start = ((ext_at + len_extensions) & 0xFFFFF800) + 0x800
"""
import os, struct

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"


class LightVpp:
    def __init__(self, path):
        self.path = path
        self.f = open(path, "rb")
        head = self.f.read(0x800)
        o = 5 + 0x14F
        (self.num, self.csize, self.lo, self.lf, self.le) = struct.unpack_from("<iiiii", head, o)
        self.names_at = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.lf) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.le) & 0xFFFFF800) + 0x800
        # 读条目表
        self.f.seek(0x800)
        self.raw = self.f.read(self.num * 28)

    def entries(self):
        out = []
        for i in range(self.num):
            e = i * 28
            if e + 28 > len(self.raw):
                break
            a, b, c, body, size, m1, z = struct.unpack_from("<IIiiiii", self.raw, e)
            out.append(dict(idx=i, name_off=a, ext_off=b, body=body, size=size))
        return out

    def name(self, ent):
        self.f.seek(self.names_at + ent["name_off"])
        s = b""
        while True:
            ch = self.f.read(1)
            if not ch or ch == b"\x00":
                break
            s += ch
        return s.decode("ascii", "replace")

    def ext(self, ent):
        if not ent["ext_off"]:
            return ""
        self.f.seek(self.ext_at + ent["ext_off"])
        s = b""
        while True:
            ch = self.f.read(1)
            if not ch or ch == b"\x00":
                break
            s += ch
        return s.decode("ascii", "replace")

    def read(self, ent):
        self.f.seek(self.data_start + ent["body"])
        return self.f.read(ent["size"])

    def close(self):
        self.f.close()


for fn in ("common.vpp_pc", "textures.vpp_pc", "pegs.vpp_pc"):
    p = os.path.join(G, fn)
    v = LightVpp(p)
    print("=== %s ===" % fn)
    print("  %d 条目, %d 字节" % (v.num, os.path.getsize(p)))
    print("  names_at=0x%X ext_at=0x%X data_start=0x%X" % (v.names_at, v.ext_at, v.data_start))
    hits = []
    for e in v.entries():
        nm = v.name(e)
        if "fnt_" in nm or "font" in nm.lower() or "vint" in nm.lower():
            hits.append((nm, v.ext(e), e["size"], e["body"], e["idx"]))
    print("  字体/相关条目 %d 个:" % len(hits))
    for nm, ex, sz, body, idx in sorted(hits):
        print("    #%-6d %-26s %-10s %9d  body=0x%X" % (idx, nm, ex or "-", sz, body))
    v.close()
    print()
