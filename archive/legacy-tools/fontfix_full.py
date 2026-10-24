# -*- coding: utf-8 -*-
"""完整修复：把 fnt_body_n / fnt_body_s 的【三件套】全换成中文。

三件套
    ① common.vpp_pc   : fnt_body_n.vf3_pc / fnt_body_s.vf3_pc  -> 中文字形度量 (N=2838)
    ② textures.vpp_pc : fnt_body_n / fnt_body_s 图集          -> 中文图集 (4194304 B)
    ③ pegs.vpp_pc     : fnt_body_n / fnt_body_s 描述符        -> 中文规格

安全设计
    ★ 全部使用【追加式替换】：新数据写到文件末尾，只改条目表的
      body_off(+12) 与 size(+16)，再更新 container_size。
      原数据留在文件里成为死数据，引擎不会读。
    ★ 不重排、不重建、不动条目顺序 => VPP 结构绝对安全。
    ★ textures.vpp_pc 只追加约 11.7 MB（1.26 GB -> 1.27 GB）。

用法
    python fontfix_full.py apply
    python fontfix_full.py restore
    python fontfix_full.py status
"""
import os, sys, struct, shutil, datetime, hashlib, glob

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BACKUP = r"F:\sr2-cn\_fontfix_backup"
REF = "fnt_chinese"
TARGETS = ["fnt_body_n", "fnt_body_s"]


def md5_file(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


class RWvpp:
    """可读写 VPP：读头 + 条目表常驻，body 按需 seek。支持追加式替换。"""

    def __init__(self, path):
        self.path = path
        self.f = open(path, "r+b")
        head = self.f.read(0x800)
        o = 5 + 0x14F
        (self.num, self.csize, self.lo, self.lf, self.le) = struct.unpack_from("<iiiii", head, o)
        self.names_at = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.lf) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.le) & 0xFFFFF800) + 0x800
        self.csize_off = o + 4
        self.f.seek(0x800)
        self.raw = self.f.read(self.num * 28)

    def entries(self):
        out = []
        for i in range(self.num):
            e = i * 28
            if e + 28 > len(self.raw):
                break
            a, b, c, body, size, m1, z = struct.unpack_from("<IIiiiii", self.raw, e)
            out.append(dict(idx=i, entry_off=0x800 + e, name_off=a, ext_off=b,
                            body=body, size=size))
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
        return self._strz(self.ext_at, ent["ext_off"]) if ent["ext_off"] else ""

    def read(self, ent):
        self.f.seek(self.data_start + ent["body"])
        return self.f.read(ent["size"])

    def append(self, payload, align=0x800):
        self.f.seek(0, os.SEEK_END)
        cur = self.f.tell()
        pad = (-cur) % align
        if pad:
            self.f.write(b"\x00" * pad)
            cur += pad
        new_body = cur - self.data_start
        self.f.write(payload)
        new_size = self.f.tell()
        # 更新 container_size
        self.f.seek(self.csize_off)
        self.f.write(struct.pack("<i", new_size))
        self.f.flush()
        return new_body

    def repoint(self, ent, nb, ns):
        self.f.seek(ent["entry_off"] + 12)
        self.f.write(struct.pack("<i", nb))
        self.f.seek(ent["entry_off"] + 16)
        self.f.write(struct.pack("<i", ns))
        self.f.flush()

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def find(v, name, ext=None):
    for e in v.entries():
        if v.name(e) == name and (ext is None or v.ext(e) == ext):
            return e
    return None


def status():
    print("=== 文件 md5 ===")
    for f in ("common.vpp_pc", "textures.vpp_pc", "pegs.vpp_pc", "patch.vpp_pc"):
        p = os.path.join(G, f)
        print("  %-18s %13d  %s" % (f, os.path.getsize(p), md5_file(p)[:20]))
    print()
    print("=== 字体三件套 ===")
    with LightVpp(os.path.join(G, "common.vpp_pc")) as v:
        print("  common (vf3 度量):")
        for e in v.entries():
            nm = v.name(e)
            if nm in TARGETS + [REF] and v.ext(e) == "vf3_pc":
                d = v.read(e)
                N, = struct.unpack_from("<i", d, 0x08)
                print("    %-14s size=%-7d N=%-6d %s" % (nm, e["size"], N,
                                                         "★ 中文" if N == 2838 else "ASCII"))
    with LightVpp(os.path.join(G, "textures.vpp_pc")) as v:
        print("  textures (图集):")
        for e in v.entries():
            nm = v.name(e)
            if nm in TARGETS + [REF]:
                print("    %-14s size=%-9d %s" % (nm, e["size"],
                                                  "★ 中文(4MB)" if e["size"] == 4194304 else "英文"))
    with LightVpp(os.path.join(G, "pegs.vpp_pc")) as v:
        print("  pegs (描述符):")
        for e in v.entries():
            nm = v.name(e)
            if nm in TARGETS + [REF]:
                d = v.read(e)
                i = d.find(b"fnt_")
                print("    %-14s size=%-4d 字段=%s %s" %
                      (nm, e["size"], d[0x0C:0x20].hex(" "),
                       d[i:].rstrip(b"\x00").decode("latin1")))


def apply():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ok = True

    # ---------- 读取参考数据 ----------
    with LightVpp(os.path.join(G, "common.vpp_pc")) as cv:
        ref_vf3 = cv.read(find(cv, REF, "vf3_pc"))
    with LightVpp(os.path.join(G, "textures.vpp_pc")) as tv:
        ref_atlas = tv.read(find(tv, REF))
    with LightVpp(os.path.join(G, "pegs.vpp_pc")) as pv:
        ref_desc = pv.read(find(pv, REF))
    print("参考数据: vf3=%d B, atlas=%d B, desc=%d B" %
          (len(ref_vf3), len(ref_atlas), len(ref_desc)))

    # ---------- ① common.vpp_pc : vf3 ----------
    cp = os.path.join(G, "common.vpp_pc")
    shutil.copy2(cp, os.path.join(BACKUP, "common.vpp_pc.before_full_%s" % ts))
    with RWvpp(cp) as v:
        nb = v.append(ref_vf3)
        for t in TARGETS:
            e = find(v, t, "vf3_pc")
            if e is None:
                print("  ★ 找不到 %s.vf3_pc" % t); ok = False; continue
            print("  common: %-14s.vf3_pc  size %d -> %d" % (t, e["size"], len(ref_vf3)))
            v.repoint(e, nb, len(ref_vf3))
    print("  common.vpp_pc md5 -> %s" % md5_file(cp)[:20])
    print()

    # ---------- ② textures.vpp_pc : 图集 ----------
    tp = os.path.join(G, "textures.vpp_pc")
    tbak = os.path.join(BACKUP, "textures.vpp_pc.before_full_%s" % ts)
    if not os.path.exists(tbak):
        print("  备份 textures.vpp_pc（1.26 GB，请稍候）...")
        shutil.copy2(tp, tbak)
    with RWvpp(tp) as v:
        nb = v.append(ref_atlas)
        for t in TARGETS:
            e = find(v, t)
            if e is None:
                print("  ★ 找不到 %s 图集" % t); ok = False; continue
            print("  textures: %-14s 图集  size %d -> %d" % (t, e["size"], len(ref_atlas)))
            v.repoint(e, nb, len(ref_atlas))
    print("  textures.vpp_pc md5 -> %s" % md5_file(tp)[:20])
    print()

    # ---------- ③ pegs.vpp_pc : 描述符 ----------
    pp = os.path.join(G, "pegs.vpp_pc")
    shutil.copy2(pp, os.path.join(BACKUP, "pegs.vpp_pc.before_full_%s" % ts))
    with RWvpp(pp) as v:
        i = ref_desc.find(b"fnt_")
        head = ref_desc[:i]
        for t in TARGETS:
            e = find(v, t)
            if e is None:
                print("  ★ 找不到 %s 描述符" % t); ok = False; continue
            newname = t + "_nobdr.tga"
            blob = bytearray(head) + newname.encode() + b"\x00"
            if len(blob) % 8:
                blob += b"\x00" * (8 - len(blob) % 8)
            struct.pack_into("<I", blob, 0x08, len(blob))
            nb = v.append(bytes(blob))
            print("  pegs: %-14s 描述符 %d -> %d 字节" % (t, e["size"], len(blob)))
            v.repoint(e, nb, len(blob))
    print("  pegs.vpp_pc md5 -> %s" % md5_file(pp)[:20])
    print()

    print("=== 完成 ===" if ok else "=== 有错误 ===")
    print()
    status()


def restore():
    print("=== 回滚 ===")
    for f in ("common.vpp_pc", "textures.vpp_pc", "pegs.vpp_pc", "patch.vpp_pc"):
        cands = sorted(glob.glob(os.path.join(BACKUP, f + ".before_*")))
        if not cands:
            print("  %-18s 无备份" % f)
            continue
        src = cands[0]
        print("  %-18s <- %s" % (f, os.path.basename(src)))
        shutil.copy2(src, os.path.join(G, f))
    print()
    status()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"status": status, "apply": apply, "restore": restore}[cmd]()
