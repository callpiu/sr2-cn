# -*- coding: utf-8 -*-
"""字体修复候选 v2：更激进 —— 把所有 CJK 字体槽位都换成中文数据。

背景
    v1 只换了 fnt_body_n / fnt_body_s，实测字幕无变化。
    说明字幕用的不是这两个（或不止这两个）。

本版
    把【所有】非中文的「图层字体」也换掉：
        fnt_bodyital_n / fnt_bodyital_s / fnt_head_n / fnt_head_s
    即别名表里的：
        thin            -> (fnt_body_n, -1)
        thin_overlay    -> (fnt_body_n, fnt_body_s)
        header_n        -> (?, -1)
        header_n_overlay-> (?, ?)
        bodyital_overlay-> (fnt_bodyital_n, fnt_bodyital_s)

    做法与 v1 相同：改 common.vpp_pc 的 vf3 + pegs.vpp_pc 的描述符。

用法
    python fontfix_v2.py apply
    python fontfix_v2.py restore
    python fontfix_v2.py status
"""
import os, sys, struct, shutil, datetime, glob, hashlib

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BACKUP = r"F:\sr2-cn\_fontfix_backup"
REF = "fnt_chinese"
# 要替换的目标（全部 CJK 转 ASCII 的字体）
TARGETS = ["fnt_body_n", "fnt_body_s",
           "fnt_bodyital_n", "fnt_bodyital_s",
           "fnt_head_n", "fnt_head_s"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


class FullVpp:
    def __init__(self, path):
        self.path = path
        self.data = bytearray(open(path, "rb").read())
        d = self.data
        o = 5 + 0x14F
        (self.num, self.csize, self.lo, self.lf, self.le) = struct.unpack_from("<iiiii", d, o)
        self.names_at = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.lf) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.le) & 0xFFFFF800) + 0x800
        self.csize_off = o + 4

    def entries(self):
        out = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b, c, body, size, m1, z = struct.unpack_from("<IIiiiii", self.data, e)
            out.append(dict(idx=i, entry_off=e, name_off=a, ext_off=b,
                            body=body, size=size))
        return out

    def _strz(self, base, off):
        e = self.data.find(b"\x00", base + off)
        return self.data[base + off:e].decode("ascii", "replace")

    def name(self, ent):
        return self._strz(self.names_at, ent["name_off"])

    def ext(self, ent):
        return self._strz(self.ext_at, ent["ext_off"]) if ent["ext_off"] else ""

    def read(self, ent):
        p = self.data_start + ent["body"]
        return bytes(self.data[p:p + ent["size"]])

    def append_body(self, payload, align=0x800):
        d = self.data
        pad = (-len(d)) % align
        d += b"\x00" * pad
        new_body = len(d) - self.data_start
        d += payload
        struct.pack_into("<i", d, self.csize_off, len(d))
        return new_body

    def repoint(self, ent, new_body, new_size):
        struct.pack_into("<i", self.data, ent["entry_off"] + 12, new_body)
        struct.pack_into("<i", self.data, ent["entry_off"] + 16, new_size)

    def save(self, path=None):
        open(path or self.path, "wb").write(bytes(self.data))


def find(v, name, ext=None):
    for e in v.entries():
        if v.name(e) == name and (ext is None or v.ext(e) == ext):
            return e
    return None


def status():
    print("=== 文件状态 ===")
    for f in ("common.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc", "patch.vpp_pc"):
        p = os.path.join(G, f)
        print("  %-18s %12d  %s" % (f, os.path.getsize(p), md5(p)[:16]))
    print()
    print("=== 字体度量 (common.vpp_pc) ===")
    with LightVpp(os.path.join(G, "common.vpp_pc")) as v:
        for e in v.entries():
            nm = v.name(e)
            if nm.startswith("fnt_") and v.ext(e) == "vf3_pc":
                d = v.read(e)
                N, = struct.unpack_from("<i", d, 0x08)
                tag = "★ 中文" if N == 2838 else ("ASCII" if N == 224 else "其它")
                print("  %-18s size=%-7d N=%-6d %s" % (nm, e["size"], N, tag))


def apply_v2():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ok = True

    # ---- common.vpp_pc ----
    cp = os.path.join(G, "common.vpp_pc")
    cbak = os.path.join(BACKUP, "common.vpp_pc.before_v2_%s" % ts)
    shutil.copy2(cp, cbak)
    cv = FullVpp(cp)
    ref_vf3 = cv.read(find(cv, REF, "vf3_pc"))
    print("参考 vf3: %d 字节, N=%d" % (len(ref_vf3), struct.unpack_from("<i", ref_vf3, 0x08)[0]))
    body_vf3 = cv.append_body(ref_vf3)
    for t in TARGETS:
        e = find(cv, t, "vf3_pc")
        if e is None:
            continue
        print("  %-18s vf3: %d -> %d 字节" % (t, e["size"], len(ref_vf3)))
        cv.repoint(e, body_vf3, len(ref_vf3))
    cv.save()
    print("  common.vpp_pc -> %s" % md5(cp))
    print()

    # ---- pegs.vpp_pc ----
    pp = os.path.join(G, "pegs.vpp_pc")
    pbak = os.path.join(BACKUP, "pegs.vpp_pc.before_v2_%s" % ts)
    shutil.copy2(pp, pbak)
    pv = FullVpp(pp)
    ref_desc = pv.read(find(pv, REF))
    i = ref_desc.find(b"fnt_")
    fixed_part = ref_desc[:i]
    print("参考描述符: 固定部分 %d 字节" % len(fixed_part))
    for t in TARGETS:
        e = find(pv, t)
        if e is None:
            continue
        newname = t + "_nobdr.tga"
        blob = bytearray(fixed_part) + newname.encode() + b"\x00"
        if len(blob) % 8:
            blob += b"\x00" * (8 - len(blob) % 8)
        struct.pack_into("<I", blob, 0x08, len(blob))
        nb = pv.append_body(bytes(blob))
        old = pv.read(e)
        oi = old.find(b"fnt_")
        print("  %-18s 描述符 %d -> %d 字节 (%s)" %
              (t, len(old), len(blob), old[oi:].rstrip(b"\x00").decode("latin1")))
        pv.repoint(e, nb, len(blob))
    pv.save()
    print("  pegs.vpp_pc -> %s" % md5(pp))
    print()
    status()


def restore():
    files = {}
    for f in os.listdir(BACKUP):
        for base in ("common.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc", "patch.vpp_pc"):
            if f == base or f.startswith(base + ".before_"):
                if base not in files or f < files[base]:
                    files[base] = f
    for base, f in files.items():
        shutil.copy2(os.path.join(BACKUP, f), os.path.join(G, base))
        print("还原 %-18s <- %s" % (base, f))
    print()
    status()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"status": status, "apply": apply_v2, "restore": restore}[cmd]()
