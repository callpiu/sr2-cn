# -*- coding: utf-8 -*-
# 用「屏幕实际显示的 UV」反查引擎读的是哪一份 vf3
import os, re, struct

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])


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


def load_tables(pkg):
    v = Vpp(os.path.join(G, pkg))
    b = v.read(v.find("fnt_chinese", "vf3_pc"))
    N = struct.unpack_from("<I", b, 8)[0]
    u_off = 0xD0 + N * 16
    v_off = u_off + N * 4
    U = []
    V = []
    for i in range(N):
        U.append(struct.unpack_from("<i", b, u_off + i * 4)[0])
        if v_off + i * 4 + 4 <= len(b):
            V.append(struct.unpack_from("<i", b, v_off + i * 4)[0])
        else:
            V.append(None)
    return N, U, V


tabs = {}
for pkg in ["common.vpp_pc", "patch.vpp_pc"]:
    N, U, V = load_tables(pkg)
    tabs[pkg] = (N, U, V)
    print("[%s] N=%d" % (pkg, N))

# 汉化/官方 charlist（patch 内的 charlist_CH）
v = Vpp(os.path.join(G, "patch.vpp_pc"))
clb = v.read(v.find("charlist_CH", "txt"))
m = re.search(rb"count\s*=\s*(\d+)", clb)
body = clb[m.end():] if m else clb
end = body.find(b"//ENDOFFILE")
CL = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
print("charlist_CH 条目 =", len(CL))


def ch(i):
    return chr(CL[i]) if 0 <= i < len(CL) else "?"


# 对方文档给出的「屏幕实际显示」的 UV
OBS = [("使", 590, 125), ("發", 1055, 807), ("光", 869, 156)]
# 期望字（官方繁中记录 0x10AF1E62 = 兄弟們正要去進行交易…）
EXPECT = "兄弟們正要去進行交易保護他們避免受到攻擊"

print("\n=== 用观察到的 UV 反查索引 ===")
for name, U, V in [(k, tabs[k][1], tabs[k][2]) for k in tabs]:
    print("\n-- 表: %s --" % name)
    pair = {}
    for i in range(len(U)):
        if V[i] is not None:
            pair.setdefault((U[i], V[i]), []).append(i)
    for chname, u, vv in OBS:
        hit = pair.get((u, vv), [])
        if hit:
            desc = ", ".join("索引%d=%s" % (i, ch(i)) for i in hit[:6])
            print("   显示字「%s」UV=(%d,%d) → %s" % (chname, u, vv, desc))
        else:
            print("   显示字「%s」UV=(%d,%d) → 该表中不存在此 UV 对" % (chname, u, vv))

print("\n=== 反向：期望字在本表里的 UV ===")
for name, U, V in [(k, tabs[k][1], tabs[k][2]) for k in tabs]:
    print("\n-- 表: %s --" % name)
    pos = {}
    for i, c in enumerate(CL):
        pos.setdefault(c, i)
    for c in EXPECT[:10]:
        i = pos.get(ord(c))
        if i is None:
            print("   %s 不在 charlist" % c); continue
        u = U[i] if i < len(U) else None
        vv = V[i] if i < len(V) else None
        print("   期望字「%s」charlist索引=%-5d → U=%-6s V=%-6s" % (c, i, u, vv))
