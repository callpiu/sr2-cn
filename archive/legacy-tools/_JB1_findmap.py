# -*- coding: utf-8 -*-
# 核心实验：找出「字符 -> 引擎输出索引」的映射表 f
# 已知：引擎对「你的兄弟們需要你的保護」输出索引序列
#   J = [336,1784,410,967,362,2656,2268,336,1784,354,2342]
# 若某张表 T 满足 T[336]=你, T[1784]=的, ... 则 T 就是引擎的映射源
import os, re, struct, glob

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


def load_cl_bytes(b):
    m = re.search(rb"count\s*=\s*(\d+)", b)
    body = b[m.end():] if m else b
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


CHARS = "你的兄弟們需要保護"
J = [336, 1784, 410, 967, 362, 2656, 2268, 336, 1784, 354, 2342]
# 期望映射（每个字符 -> 引擎输出索引）
WANT = {}
for c, i in zip("你的兄弟們需要保護", [336, 1784, 410, 967, 362, 2656, 2268, 354, 2342]):
    WANT[c] = i
print("目标映射 WANT =", {k: v for k, v in WANT.items()})


def bsearch(arr, key):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == key:
            return mid
        if arr[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def analyze(tag, CL):
    print("\n" + "=" * 70)
    print("表: %s   长度=%d" % (tag, len(CL)))
    if not CL:
        return
    print("  前12项:", CL[:12])
    print("  是否升序:", all(CL[i] <= CL[i + 1] for i in range(len(CL) - 1)))
    print("  唯一项数:", len(set(CL)))
    # 直接索引
    direct = {}
    for c in WANT:
        cp = ord(c)
        direct[c] = CL.index(cp) if cp in CL else None
    print("  [假设1] 字符在表中的位置(index):", direct)
    print("          是否 == WANT:", direct == WANT)
    # 二分查找
    bs = {c: bsearch(CL, ord(c)) for c in WANT}
    print("  [假设2] 二分查找结果            :", bs)
    print("          是否 == WANT:", bs == WANT)
    # 反查：CL[336] 等
    print("  [反查] CL[336]=%s CL[1784]=%s CL[410]=%s" % (
        chr(CL[336]) if 336 < len(CL) else "?",
        chr(CL[1784]) if 1784 < len(CL) else "?",
        chr(CL[410]) if 410 < len(CL) else "?"))


# 收集所有可用的 charlist
sources = []
for p in [os.path.join(G, "patch.vpp_pc"), os.path.join(G, "common.vpp_pc"),
          os.path.join(G, "textures.vpp_pc"), os.path.join(G, "pegs.vpp_pc")]:
    if os.path.exists(p):
        sources.append(p)
sources += sorted(glob.glob(r"F:/sr2-cn/_backup_*/patch.vpp_pc*"))
sources += sorted(glob.glob(r"F:/sr2-cn/pristine/patch.vpp_pc*"))
sources += sorted(glob.glob(r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/**/patch.vpp_pc", recursive=True))

seen = set()
for p in sources:
    try:
        v = Vpp(p)
        ents = v.entries()
    except Exception as ex:
        print("[跳过] %s : %s" % (p, ex))
        continue
    for e in ents:
        if "charlist" not in e["name"].lower():
            continue
        key = (p, e["name"], e["ext"])
        if key in seen:
            continue
        seen.add(key)
        try:
            CL = load_cl_bytes(v.read(e))
        except Exception as ex:
            print("[读取失败] %s / %s : %s" % (p, e["name"], ex))
            continue
        analyze("%s :: %s.%s" % (os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p),
                                 e["name"], e["ext"]), CL)
