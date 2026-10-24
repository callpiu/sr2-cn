# -*- coding: utf-8 -*-
# 测：引擎的表 M 是否 == 某个「原始 charlist」（pristine / backup_original / 汉化）
import os, re, struct, glob

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"


class Vpp:
    def __init__(self, path):
        self.d = open(path, "rb").read()
        o = 5 + 0x14F
        self.num = struct.unpack_from("<i", self.d, o)[0]
        self.lo = struct.unpack_from("<i", self.d, o + 8)[0]
        self.lf = struct.unpack_from("<i", self.d, o + 12)[0]
        self.le = struct.unpack_from("<i", self.d, o + 16)[0]
        self.na = ((0x800 + self.lo) & 0xFFFFF800) + 0x800
        self.ea = ((self.na + self.lf) & 0xFFFFF800) + 0x800
        self.ds = ((self.ea + self.le) & 0xFFFFF800) + 0x800

    def z(self, b, p):
        e = self.d.find(b"\x00", b + p)
        return self.d[b + p:e].decode("ascii", "replace")

    def ents(self):
        r = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b_, c, dd, ln = struct.unpack_from("<IIiii", self.d, e)
            r.append(dict(n=self.z(self.na, a), x=self.z(self.ea, b_) if b_ else "", o=dd, z=ln))
        return r

    def rd(self, e):
        p = self.ds + e["o"]
        return self.d[p:p + e["z"]]

    def find(self, n, x=None):
        for e in self.ents():
            if e["n"].lower() == n.lower() and (x is None or e["x"].lower() == x.lower()):
                return e
        return None


def load_cl(v, fname="charlist_CH"):
    e = v.find(fname, "txt")
    if not e:
        return None
    b = v.rd(e)
    m = re.search(rb"count\s*=\s*(\d+)", b)
    body = b[m.end():] if m else b
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]


B = load_cl(Vpp(r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2"))
TARGET = {}
for a, b in [("交", "乱"), ("他", "亡"), ("你", "任"), ("保", "伪"), ("們", "位"),
             ("兄", "偶"), ("免", "像"), ("到", "冰"), ("去", "勾"), ("受", "匪"),
             ("弟", "巧"), ("擊", "拮"), ("攻", "挺"), ("易", "携"), ("正", "校"),
             ("的", "璨"), ("要", "衡"), ("護", "该"), ("行", "貌"), ("進", "远"),
             ("避", "通"), ("需", "雄")]:
    TARGET[ord(a)] = B.index(ord(b))

paths = [os.path.join(G, "patch.vpp_pc"),
         r"F:/sr2-cn/pristine/patch.vpp_pc",
         r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/backup_original/patch.vpp_pc"]
paths += sorted(glob.glob(r"F:/sr2-cn/_backup_*/patch.vpp_pc*"))
paths += sorted(glob.glob(r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/*/patch.vpp_pc"))

seen = set()
for p in paths:
    if not os.path.exists(p):
        continue
    try:
        v = Vpp(p)
        CL = load_cl(v)
    except Exception as ex:
        print("[跳过] %s : %s" % (p, ex))
        continue
    if not CL:
        continue
    key = (len(CL), tuple(CL[:5]))
    tag = p.replace("F:/sr2-cn/", "")
    hit = 0
    det = []
    for cp, want in TARGET.items():
        try:
            got = CL.index(cp)
        except ValueError:
            got = None
        if got == want:
            hit += 1
        if len(det) < 6:
            det.append("%s:%s/%s" % (chr(cp), got, want))
    print("%-52s len=%-6d 命中=%2d/22  %s" % (tag, len(CL), hit, " ".join(det)))
