# -*- coding: utf-8 -*-
"""决定性诊断：把【全部 CJK 字体的度量表】都换成同一个已知序列。

原理
    如果字幕用的是这些字体中的【任意一个】，那么它的度量表被我换成
    「前 2838 个字全部指向同一个醒目字形」之后，
    字幕必然显示成一串【完全相同的字】—— 一眼可辨。

    如果字幕毫无变化 -> 字幕用的字体【不在这批里】。

做法
    1. 构造一个「全部汉字映射到同一个字形」的 vf3：
       - N = 2838（与中文字表项数一致）
       - 每个 glyf 记录的宽度都一样
       - U/V 全部指向图集的同一个格子（选一个笔画明显的格子）
    2. 替换 common.vpp_pc 里全部 fnt_* 的 vf3_pc
    3. pegs.vpp_pc 的描述符全部改成中文规格
    4. textures.vpp_pc 不动（图集复用现有 fnt_chinese）

用法
    python diag_allfonts.py apply
    python diag_allfonts.py restore
"""
import os, sys, struct, shutil, datetime, hashlib, glob

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BACKUP = r"F:\sr2-cn\_fontfix_backup"
REF = "fnt_chinese"
ALLFONTS = ["fnt_body_n", "fnt_body_s", "fnt_bodyital_n", "fnt_bodyital_s",
            "fnt_head_n", "fnt_head_s", "fnt_cz", "fnt_cz_s", "fnt_korea"]


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
            out.append(dict(idx=i, entry_off=e, name_off=a, ext_off=b, body=body, size=size))
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
        d += b"\x00" * ((-len(d)) % align)
        nb = len(d) - self.data_start
        d += payload
        struct.pack_into("<i", d, self.csize_off, len(d))
        return nb

    def repoint(self, ent, nb, ns):
        struct.pack_into("<i", self.data, ent["entry_off"] + 12, nb)
        struct.pack_into("<i", self.data, ent["entry_off"] + 16, ns)

    def save(self):
        open(self.path, "wb").write(bytes(self.data))


def find(v, name, ext=None):
    for e in v.entries():
        if v.name(e) == name and (ext is None or v.ext(e) == ext):
            return e
    return None


def build_uniform_vf3():
    """构造：N=2838，所有字形都指向图集格 (U=100, V=100)，宽度统一。

    vf3 结构（来自快照）：
        +0x00  magic?      (2 字节)
        +0x02  ?           (2 字节)
        +0x04  ver         u32 = 2
        +0x08  N           i32
        +0x0C  firstascii  i32 = 32
        +0x10  W           i32
        +0x14  H           i16
        +0x16  RenderH     i16
        +0x18  BasOff      i32
        +0x1C  CharSpacing i16
        +0x1E  ?           i16 = 0
        +0x20  KernPairs   i32
        +0x24  VertOff     i32
        +0x28  PegName     char[64]
        +0x68  BitmapName  char[64]
        +0xA8  ?           (到 0xD0)
        0xD0   FontCharacter × N  (16 B each)
        0xD0+N*16  U[] × N (i32)
        ...        V[] × ...
    """
    N = 2838
    hdr = bytearray(0xD0)
    struct.pack_into("<I", hdr, 0x04, 2)          # ver
    struct.pack_into("<i", hdr, 0x08, N)          # N
    struct.pack_into("<i", hdr, 0x0C, 32)         # firstascii
    struct.pack_into("<i", hdr, 0x10, 29)         # W
    struct.pack_into("<h", hdr, 0x14, 37)         # H
    struct.pack_into("<h", hdr, 0x16, 28)         # RenderH
    struct.pack_into("<i", hdr, 0x18, 0)          # BasOff
    struct.pack_into("<h", hdr, 0x1C, -5)         # CharSpacing
    struct.pack_into("<i", hdr, 0x20, 0)          # KernPairs
    struct.pack_into("<i", hdr, 0x24, 4)          # VertOff
    name = b"fnt_chinese.peg"
    hdr[0x28:0x28 + len(name)] = name
    bmp = b"fnt_chinese_nobdr.tga"
    hdr[0x68:0x68 + len(bmp)] = bmp

    # FontCharacter: [width, 0, 0, 0, -1, 0, width, 0] (16 B)
    recs = bytearray()
    for i in range(N):
        recs += struct.pack("<hhhhhhhh", 29, 0, 0, 0, -1, 0, 29, 0)

    # U/V：全部指向同一个格子（选 一 的位置附近；用 (1365, 94) = 一）
    U = struct.pack("<%di" % N, *([1365] * N))
    V = struct.pack("<%di" % (N - 5), *([94] * (N - 5)))
    return bytes(hdr) + bytes(recs) + U + V


def apply():
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    blob = build_uniform_vf3()
    print("构造统一 vf3: %d 字节" % len(blob))

    # ---- common.vpp_pc ----
    cp = os.path.join(G, "common.vpp_pc")
    shutil.copy2(cp, os.path.join(BACKUP, "common.vpp_pc.before_diag_%s" % ts))
    cv = FullVpp(cp)
    nb = cv.append_body(blob)
    n = 0
    for t in ALLFONTS + [REF]:
        e = find(cv, t, "vf3_pc")
        if e is None:
            continue
        cv.repoint(e, nb, len(blob))
        n += 1
    cv.save()
    print("common.vpp_pc: 替换了 %d 个字体的 vf3 -> %s" % (n, md5(cp)))

    # ---- pegs.vpp_pc ----
    pp = os.path.join(G, "pegs.vpp_pc")
    shutil.copy2(pp, os.path.join(BACKUP, "pegs.vpp_pc.before_diag_%s" % ts))
    pv = FullVpp(pp)
    ref_desc = pv.read(find(pv, REF))
    i = ref_desc.find(b"fnt_")
    head = ref_desc[:i]
    m = 0
    for t in ALLFONTS + [REF]:
        e = find(pv, t)
        if e is None:
            continue
        nm = t + "_nobdr.tga"
        d2 = bytearray(head) + nm.encode() + b"\x00"
        if len(d2) % 8:
            d2 += b"\x00" * (8 - len(d2) % 8)
        struct.pack_into("<I", d2, 0x08, len(d2))
        nb2 = pv.append_body(bytes(d2))
        pv.repoint(e, nb2, len(d2))
        m += 1
    pv.save()
    print("pegs.vpp_pc: 替换了 %d 个描述符 -> %s" % (m, md5(pp)))
    print()
    print(">>> 进游戏看字幕：")
    print("    若显示一串【完全相同的字】-> 字幕用了这批字体之一（我就能精确定位）")
    print("    若完全没变 -> 字幕不用这些字体（需要换方向）")


def restore():
    for base in ("common.vpp_pc", "pegs.vpp_pc"):
        baks = sorted(glob.glob(os.path.join(BACKUP, base + ".before_diag_*")))
        if not baks:
            baks = sorted(glob.glob(os.path.join(BACKUP, base + ".before_*")))
        if baks:
            shutil.copy2(baks[0], os.path.join(G, base))
            print("还原 %-16s <- %s" % (base, os.path.basename(baks[0])))
        else:
            src = os.path.join(BACKUP, base)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(G, base))
                print("还原 %-16s <- %s" % (base, base))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "apply"
    {"apply": apply, "restore": restore}[cmd]()
