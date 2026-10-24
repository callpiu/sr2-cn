# -*- coding: utf-8 -*-
# 1) 从 exe 里抽出所有 ACT_HELI_* 字符串
# 2) 用多种 hash 算法去匹配 static_CH 里的记录 ID，确认哪条记录对应哪个字符串名
import os, re, struct, zlib

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


def records(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    po = 12 + buckets * 8
    out = []
    for idx in range(count):
        p = struct.unpack_from("<I", data, po + idx * 4)[0]
        if p + 4 > len(data):
            continue
        b4 = data[p:p + 4]
        q = p + 4
        slots = []
        while q + 2 <= len(data):
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0:
                break
            slots.append(w)
            q += 2
        out.append((idx, b4, slots))
    return out


# --- 1. exe 里的 ACT_HELI_* ---
exe = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
names = set()
for m in re.finditer(rb"ACT_HELI[A-Z0-9_]{0,48}", exe):
    names.add(m.group().decode())
names = sorted(names)
print("exe 里的 ACT_HELI_* 字符串共 %d 个：" % len(names))
for n in names:
    print("   ", n)

# --- 2. hash 尝试 ---
def fnv1a(s):
    h = 0x811C9DC5
    for c in s:
        h ^= c
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def fnv1(s):
    h = 0x811C9DC5
    for c in s:
        h = (h * 0x01000193) & 0xFFFFFFFF
        h ^= c
    return h


def volition(s):
    h = 0
    for c in s:
        h = (h * 33 + c) & 0xFFFFFFFF
    return h


def crc(s):
    return zlib.crc32(s) & 0xFFFFFFFF


HASHES = {
    "crc32": crc,
    "fnv1a": fnv1a,
    "fnv1": fnv1,
    "volition(h*33+c)": volition,
}

v = Vpp(os.path.join(G, "patch.vpp_pc"))
rows = records(v.rd(v.find("static_CH", "le_strings")))
byhash = {}
for idx, b4, slots in rows:
    byhash[b4] = (idx, slots)

TARGETS = [bytes.fromhex(h) for h in ["84F287ED", "10AF1E62", "EC2D9F07", "95A79EDC", "343FEA1F", "E52F931A"]]
print("\n目标记录 ID（文件里前 4 字节）:", [b.hex().upper() for b in TARGETS])
for b in TARGETS:
    print("  %s 在 static_CH: %s" % (b.hex().upper(), "是 idx=%d" % byhash[b][0] if b in byhash else "否"))

print("\n=== 用各 hash 算法匹配 ===")
for hn, hf in HASHES.items():
    hits = []
    for n in names:
        h = hf(n.encode())
        for b in TARGETS:
            if h == int.from_bytes(b, "big") or h == int.from_bytes(b, "little"):
                hits.append("%s -> %s" % (n, b.hex().upper()))
    print("  %-18s 命中 %d 个 %s" % (hn, len(hits), hits[:6]))
