# -*- coding: utf-8 -*-
# 核对【当前】游戏状态：patch.vpp_pc 是否原版、static_CH 里到底有什么
import os, re, struct, zlib, hashlib

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
            r.append(dict(idx=i, n=self.z(self.na, a), x=self.z(self.ea, b_) if b_ else "", o=dd, z=ln))
        return r

    def rd(self, e):
        p = self.ds + e["o"]
        return self.d[p:p + e["z"]]

    def find(self, n, x=None):
        for e in self.ents():
            if e["n"].lower() == n.lower() and (x is None or e["x"].lower() == x.lower()):
                return e
        return None


p = os.path.join(G, "patch.vpp_pc")
raw = open(p, "rb").read()
print("patch.vpp_pc  size=%d  md5=%s" % (len(raw), hashlib.md5(raw).hexdigest()))
for q in [r"F:/sr2-cn/pristine/patch.vpp_pc",
          r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014/backup_original/patch.vpp_pc",
          r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2"]:
    if os.path.exists(q):
        d2 = open(q, "rb").read()
        print("  对比 %-58s size=%-10d md5=%s  %s" % (
            os.path.basename(os.path.dirname(q)) + "/" + os.path.basename(q),
            len(d2), hashlib.md5(d2).hexdigest(), "==当前" if d2 == raw else "≠"))

v = Vpp(p)
CL_OFF = None
e = v.find("charlist_CH", "txt")
b = v.rd(e)
m = re.search(rb"count\s*=\s*(\d+)", b)
body = b[m.end():] if m else b
end = body.find(b"//ENDOFFILE")
CL = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
print("\ncharlist_CH = %d 项" % len(CL))

data = v.rd(v.find("static_CH", "le_strings"))
magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
po = 12 + buckets * 8
print("static_CH  magic=%08X ver=%d buckets=%d count=%d" % (magic, ver, buckets, count))

ids = {}
rows = []
for idx in range(count):
    q = struct.unpack_from("<I", data, po + idx * 4)[0]
    b4 = data[q:q + 4]
    w = q + 4
    slots = []
    while w + 2 <= len(data):
        s = struct.unpack_from(">H", data, w)[0]
        if s == 0:
            break
        slots.append(s)
        w += 2
    rows.append((idx, b4, slots))
    ids[int.from_bytes(b4, "big")] = idx

TARGETS = ["84F287ED", "10AF1E62", "EC2D9F07", "95A79EDC", "343FEA1F", "E52F931A"]
print("\n6 个目标 ID 是否在 static_CH：")
for t in TARGETS:
    h = int(t, 16)
    print("   %s -> %s" % (t, "idx=%d" % ids[h] if h in ids else "不在"))

# 搜「兄弟」的槽位序列
def dec(slots):
    return "".join(chr(CL[w - 0x20]) if 0 <= w - 0x20 < len(CL) else "?" for w in slots)


print("\n含『兄弟』的记录（前 8 条）：")
n = 0
for idx, b4, slots in rows:
    t = dec(slots)
    if "兄弟" in t:
        print("   %s idx=%-6d : %s" % (b4.hex().upper(), idx, t[:60]))
        n += 1
        if n >= 8:
            break
if n == 0:
    print("   无")
