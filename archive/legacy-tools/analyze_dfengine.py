# -*- coding: utf-8 -*-
"""分析 DFEngine.dll —— 游戏真正的渲染引擎，看它用什么创建字体/画文本。"""
import re
import struct
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_32

DLL = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll"
d = open(DLL, "rb").read()
print("DFEngine.dll: %d 字节" % len(d))

e = struct.unpack_from("<I", d, 0x3C)[0]
mach, nsec, _, _, _, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
opt = e + 24
base, = struct.unpack_from("<I", d, opt + 28)
imp_rva, imp_size = struct.unpack_from("<II", d, opt + 104)
secoff = opt + optsz
secs = []
for i in range(nsec):
    o = secoff + i * 40
    nm = d[o:o + 8].rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", d, o + 8)
    secs.append((nm, va, vs, rp, rs))


def r2o(rva):
    for nm, va, vs, rp, rs in secs:
        if va <= rva < va + max(vs, rs):
            return rp + (rva - va), nm
    return None, None


print("ImageBase=0x%08X" % base)
print()
print("=== DFEngine.dll 的导入表 ===")
off, _ = r2o(imp_rva)
i = 0
while off and i < 80:
    o = off + i * 20
    oft, tds, fc, name_rva, ft = struct.unpack_from("<IIIII", d, o)
    if name_rva == 0:
        break
    no, _ = r2o(name_rva)
    if no is None:
        break
    end = d.index(b"\x00", no)
    dll = d[no:end].decode()
    thunk_rva = oft if oft else ft
    to, _ = r2o(thunk_rva)
    funcs = []
    k = 0
    while to:
        v, = struct.unpack_from("<I", d, to + k * 4)
        if v == 0:
            break
        if v & 0x80000000:
            funcs.append("ord#%d" % (v & 0xFFFF))
        else:
            fo, _ = r2o(v)
            fe = d.index(b"\x00", fo + 2)
            funcs.append(d[fo + 2:fe].decode())
        k += 1
    print("  %-22s %d 个" % (dll, len(funcs)))
    KEYS = ("font", "text", "glyph", "draw", "char", "out", "string", "blt")
    hits = [f for f in funcs if any(x in f.lower() for x in KEYS)]
    if hits:
        for h in hits:
            print("      ★ %s" % h)
    i += 1
print()

print("=== DFEngine.dll 里的关键字符串 ===")
for pat in (rb"D3DXCreateFont[A-W]", rb"CreateFont[A-W]", rb"DrawText[A-W]",
            rb"TextOut[A-W]", rb"ExtTextOut[A-W]", rb"GetGlyphOutline[A-W]",
            rb"fnt_[a-z]+", rb"charlist", rb"\.vf3", rb"\.peg"):
    for m in list(re.finditer(pat, d))[:4]:
        s = d[m.start():m.start() + 40].split(b"\x00")[0]
        print("  0x%06X  %r" % (m.start(), s))
