# -*- coding: utf-8 -*-
"""正确解析 PDB 符号：
- stream 528 = /names（字符串池，每条 = u32 len + 内容 + \0）
- sym stream 525 = 符号记录；S_GPROC32/S_PUB32 里的 name 是 names 池的 u32 offset
"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb"
d = open(P, "rb").read()
info = pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl", "rb"))
BS = info["BS"]; sizes = info["sizes"]; blocks = info["blocks"]


def stream(i):
    return b"".join(d[b * BS:(b + 1) * BS] for b in blocks[i])[:sizes[i]]


names = stream(526)
print("names stream size =", len(names), "head:", names[:16].hex(" "))


def name_at(off):
    if off + 4 > len(names):
        return None
    ln = struct.unpack("<I", names[off:off + 4])[0]
    if ln > 4096:
        return None
    return names[off + 4:off + 4 + ln].decode("ascii", "replace")


# 验证：name_at(0)
print("names[0] =", repr(name_at(0)))
print("names[43] =", repr(name_at(43)))

sym = stream(525)
u32 = lambda b, o: struct.unpack("<I", b[o:o + 4])[0]
print("sym size", len(sym))

# S_PUB32 = 0x110E: payload = flags(u32) offset(u32) segment(u16) name(u32 offset)
# S_GPROC32 = 0x1108: parent(u32) end(u32) next(u32) len(u32) dbgStart(u32) dbgEnd(u32) type(u32) offset(u32) segment(u16) flags(u8) name(u32)
outs = []
off = 0
n = len(sym)
while off + 4 <= n:
    rlen = struct.unpack("<H", sym[off:off + 2])[0]
    if rlen < 2 or off + rlen > n:
        break
    rtype = struct.unpack("<H", sym[off + 2:off + 4])[0]
    p = sym[off + 4:off + rlen]
    if rtype == 0x110E and len(p) >= 14:
        seg = struct.unpack("<H", p[8:10])[0]
        noff = u32(p, 10)
        nm = name_at(noff)
        outs.append(("PUB", seg, u32(p, 4), nm))
    elif rtype == 0x1108 and len(p) >= 35:
        seg = struct.unpack("<H", p[32:34])[0]
        noff = u32(p, 34)
        nm = name_at(noff)
        outs.append(("PROC", seg, u32(p, 28), nm))
    off += rlen
    if rlen % 4:
        off += 4 - (rlen % 4)

print("decoded symbols:", len(outs))
with open(r"F:\sr2-cn\_pdb_syms2.txt", "w", encoding="utf-8") as f:
    for kind, seg, off, nm in outs:
        f.write("%s seg=%d off=0x%X %s\n" % (kind, seg, off, nm))
import re
for kw in ["MStrings", "harList", "loadchar", "Font", "font", "Glyph", "glyph", "Vint", "vint", "Localiz", "localiz"]:
    hits = [(k, s, o, nm) for k, s, o, nm in outs if nm and kw in nm]
    print("\n[%s] %d hits" % (kw, len(hits)))
    for k, s, o, nm in hits[:15]:
        print("   %s seg=%d off=0x%X %s" % (k, s, o, nm))
