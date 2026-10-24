# -*- coding: utf-8 -*-
"""字体修复 B-FULL：让 fnt_body_n / fnt_body_s 使用中文字体数据。

策略（不动 1.26 GB 的 textures.vpp_pc）
    common.vpp_pc:
        - 追加 fnt_chinese 的 vf3 (68300 B) 到文件末尾
        - 把 fnt_body_n.vf3_pc / fnt_body_s.vf3_pc 的条目 repoint 到新 body
          （=> 两者都用中文字形度量 N=2838）
    pegs.vpp_pc:
        - 构造新的描述符：以 fnt_chinese 的描述符为模板，
          文件名改回 fnt_body_n_nobdr.tga / fnt_body_s_nobdr.tga
        - 追加到文件末尾，把两个条目 repoint 过去
        - 描述符内部尺寸字段 = fnt_chinese 的（8/8/0x40）
    textures.vpp_pc:
        - 不动。图集通过条目名解析（descriptor 的 .tga 名去掉 _nobdr.tga = 条目名）

用法
    python fontfix_Bfull.py apply
    python fontfix_Bfull.py restore
    python fontfix_Bfull.py diff
"""
import os, sys, struct, shutil, datetime, hashlib

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BACKUP = r"F:\sr2-cn\_fontfix_backup"
TARGETS = ["fnt_body_n", "fnt_body_s"]
REF = "fnt_chinese"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


class FullVpp:
    """可写的完整 VPP（整文件读入内存）。用于 common(182MB) / pegs(8.8MB)。
    textures 太大不用。"""

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
                            body=body, size=size, m1=m1, z=z))
        return out

    def _strz(self, base, off):
        d = self.data
        e = d.find(b"\x00", base + off)
        return d[base + off:e].decode("ascii", "replace")

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


def diff():
    print("=== common.vpp_pc 的 vf3 ===")
    with LightVpp(os.path.join(G, "common.vpp_pc")) as v:
        for e in v.entries():
            nm = v.name(e)
            if nm in TARGETS + [REF] and v.ext(e) == "vf3_pc":
                d = v.read(e)
                N, = struct.unpack_from("<i", d, 0x08)
                print("  %-14s size=%-6d N=%-5d body=0x%X" % (nm, e["size"], N, e["body"]))
    print()
    print("=== pegs.vpp_pc 的描述符 ===")
    with LightVpp(os.path.join(G, "pegs.vpp_pc")) as v:
        for e in v.entries():
            nm = v.name(e)
            if nm in TARGETS + [REF]:
                d = v.read(e)
                i = d.find(b"fnt_")
                print("  %-14s size=%-3d 字段=%s  文件=%r" %
                      (nm, e["size"], d[:0x20].hex(" "), d[i:].rstrip(b"\x00").decode("latin1")))
    print()
    print("=== md5 ===")
    for f in ("common.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc"):
        print("  %-16s %s" % (f, md5(os.path.join(G, f))))


def apply_Bfull():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ok = True

    # ---------- 1. common.vpp_pc : 换 vf3 度量 ----------
    cp = os.path.join(G, "common.vpp_pc")
    cbak = os.path.join(BACKUP, "common.vpp_pc.before_Bfull_%s" % ts)
    if not os.path.exists(cbak):
        shutil.copy2(cp, cbak)
    print("备份: %s" % os.path.basename(cbak))
    cv = FullVpp(cp)
    ref_vf3 = find(cv, REF, "vf3_pc")
    ref_blob = cv.read(ref_vf3)
    print("参考 vf3 (fnt_chinese): %d 字节, N=%d" %
          (len(ref_blob), struct.unpack_from("<i", ref_blob, 0x08)[0]))
    new_body = cv.append_body(ref_blob)
    print("  追加到 body=0x%X" % new_body)
    for t in TARGETS:
        e = find(cv, t, "vf3_pc")
        if e is None:
            print("  ★ 找不到 %s.vf3_pc" % t); ok = False; continue
        print("  %s.vf3_pc: size %d -> %d, body 0x%X -> 0x%X" %
              (t, e["size"], len(ref_blob), e["body"], new_body))
        cv.repoint(e, new_body, len(ref_blob))
    cv.save()
    print("  common.vpp_pc 新 md5: %s" % md5(cp))
    print()

    # ---------- 2. pegs.vpp_pc : 换描述符 ----------
    pp = os.path.join(G, "pegs.vpp_pc")
    pbak = os.path.join(BACKUP, "pegs.vpp_pc.before_Bfull_%s" % ts)
    if not os.path.exists(pbak):
        shutil.copy2(pp, pbak)
    print("备份: %s" % os.path.basename(pbak))
    pv = FullVpp(pp)
    ref_desc = pv.read(find(pv, REF))
    ref_name = ref_desc[ref_desc.find(b"fnt_"):].rstrip(b"\x00").decode("latin1")
    print("参考描述符 (fnt_chinese): %d 字节, 文件=%r" % (len(ref_desc), ref_name))
    for t in TARGETS:
        e = find(pv, t)
        if e is None:
            print("  ★ 找不到 %s" % t); ok = False; continue
        old = pv.read(e)
        old_name = old[old.find(b"fnt_"):].rstrip(b"\x00").decode("latin1")
        # 以 fnt_chinese 描述符为模板，文件名换成该字体自己的
        newname = t + "_nobdr.tga"
        i = ref_desc.find(b"fnt_")
        # 描述符固定字段到 i 为止，之后是「文件名 + \0 + 补零」
        # 允许比模板更长（因为我们把它追加到文件末尾，不受原大小限制）
        blob = bytearray(ref_desc[:i]) + newname.encode() + b"\x00"
        # 补齐到 8 字节对齐（描述符惯例）
        if len(blob) % 8:
            blob += b"\x00" * (8 - len(blob) % 8)
        # 更新描述符自身的长度字段 @+0x08
        struct.pack_into("<I", blob, 0x08, len(blob))
        nb = pv.append_body(bytes(blob))
        print("  %s: 描述符 %d 字节 (%s) -> %d 字节 (%s), body 0x%X -> 0x%X" %
              (t, len(old), old_name, len(blob), newname, e["body"], nb))
        pv.repoint(e, nb, len(blob))
    pv.save()
    print("  pegs.vpp_pc 新 md5: %s" % md5(pp))
    print()

    print("=== 完成 ===" if ok else "=== 有错误 ===")
    print()
    diff()


def restore():
    files = {}
    for f in os.listdir(BACKUP):
        for base in ("common.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc"):
            if f.startswith(base + ".before_Bfull_"):
                k = base
                if k not in files or f > files[k]:
                    files[k] = f
    if not files:
        print("无 Bfull 备份")
        return
    for base, f in files.items():
        shutil.copy2(os.path.join(BACKUP, f), os.path.join(G, base))
        print("已还原 %s <- %s" % (base, f))
    print()
    diff()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "diff"
    {"diff": diff, "apply": apply_Bfull, "restore": restore}[cmd]()
