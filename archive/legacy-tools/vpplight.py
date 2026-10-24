# -*- coding: utf-8 -*-
"""轻量 VPP 读取器：只读文件头 + 条目表，按需 seek 单条目。
避免把 1.26 GB 的 textures.vpp_pc 整个读进内存。
"""
import os, struct


class LightVpp:
    MAGIC = b"\xCE\x0A\x89\x51\x04"

    def __init__(self, path):
        self.path = path
        self.f = open(path, "rb")
        head = self.f.read(0x800)
        o = 5 + 0x14F
        (self.num, self.csize, self.lo, self.lf, self.le) = struct.unpack_from("<iiiii", head, o)
        self.names_at = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.lf) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.le) & 0xFFFFF800) + 0x800
        self.f.seek(0x800)
        self.raw = self.f.read(self.num * 28)

    def entries(self):
        out = []
        for i in range(self.num):
            e = i * 28
            if e + 28 > len(self.raw):
                break
            a, b, c, body, size, m1, z = struct.unpack_from("<IIiiiii", self.raw, e)
            out.append(dict(idx=i, name_off=a, ext_off=b, body=body, size=size, m1=m1, z=z))
        return out

    def _strz(self, base, off):
        self.f.seek(base + off)
        s = b""
        while True:
            ch = self.f.read(1)
            if not ch or ch == b"\x00":
                break
            s += ch
        return s.decode("ascii", "replace")

    def name(self, ent):
        return self._strz(self.names_at, ent["name_off"])

    def ext(self, ent):
        if not ent["ext_off"]:
            return ""
        return self._strz(self.ext_at, ent["ext_off"])

    def read(self, ent):
        self.f.seek(self.data_start + ent["body"])
        return self.f.read(ent["size"])

    def absolute_body(self, ent):
        return self.data_start + ent["body"]

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def parse_vf3_header(d):
    """解析 vf3 头部（0x30 字节 + 可选的 kerning 对）。"""
    ver, = struct.unpack_from("<I", d, 0x04)
    N, = struct.unpack_from("<i", d, 0x08)
    firstascii, = struct.unpack_from("<i", d, 0x0C)
    W, = struct.unpack_from("<i", d, 0x10)
    H, = struct.unpack_from("<h", d, 0x14)
    RH, = struct.unpack_from("<h", d, 0x16)
    BO, = struct.unpack_from("<i", d, 0x18)
    CS, = struct.unpack_from("<h", d, 0x1C)
    nkern, = struct.unpack_from("<i", d, 0x20)
    VO, = struct.unpack_from("<i", d, 0x24)
    return dict(ver=ver, N=N, firstascii=firstascii, W=W, H=H, RenderH=RH,
                BaseOff=BO, CharSpacing=CS, KernPairs=nkern, VertOff=VO)


def parse_peg_desc(d):
    """解析 pegs 描述符（'PEG' 或 'PEG2' 头）。"""
    out = {}
    if len(d) < 8:
        return out
    tag = d[:4]
    out["tag"] = tag
    if tag in (b"PEG\x00", b"PEG2", b"PEG "):
        pass
    return out
