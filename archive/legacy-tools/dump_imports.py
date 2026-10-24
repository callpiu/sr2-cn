# -*- coding: utf-8 -*-
"""解析 SR2_pc.exe 的导入表，找出它从 dinput8.dll 需要哪些函数。"""
import struct
import os

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
e = struct.unpack_from("<I", d, 0x3C)[0]
mach, nsec, _, _, _, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
opt = e + 24
secoff = opt + optsz
secs = []
for i in range(nsec):
    o = secoff + i * 40
    nm = d[o:o + 8].rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", d, o + 8)
    secs.append((nm, va, vs, rp, rs))


def rva2off(r):
    for nm, va, vs, rp, rs in secs:
        if va <= r < va + max(vs, rs):
            return rp + (r - va)
    return None


imp_rva, imp_size = struct.unpack_from("<II", d, opt + 104)
print("导入表 RVA=0x%X size=%d" % (imp_rva, imp_size))
print()
off = rva2off(imp_rva)
i = 0
while True:
    o = off + i * 20
    oft, tds, fc, name_rva, ft = struct.unpack_from("<IIIII", d, o)
    if name_rva == 0:
        break
    no = rva2off(name_rva)
    end = d.index(b"\x00", no)
    dll = d[no:end].decode()
    # 读 thunk 表
    thunk_rva = oft if oft else ft
    to = rva2off(thunk_rva)
    funcs = []
    k = 0
    while True:
        v, = struct.unpack_from("<I", d, to + k * 4)
        if v == 0:
            break
        if v & 0x80000000:
            funcs.append("ord#%d" % (v & 0xFFFF))
        else:
            fo = rva2off(v)
            fe = d.index(b"\x00", fo + 2)
            funcs.append(d[fo + 2:fe].decode())
        k += 1
    print("  %-20s %d 个导入" % (dll, len(funcs)))
    if dll.lower().startswith("dinput8"):
        print("      ★ %s" % funcs)
    i += 1
    if i > 60:
        break
print()
print("总导入 DLL 数: %d" % i)
