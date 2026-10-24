# -*- coding: utf-8 -*-
"""提取 PDB 符号：DBI stream -> symStream(524) -> 扫 S_PUB32/S_GPROC32 找 MStrings/font/charlist。
同时把 /names 流(stream 7?)里的字符串表也 dump 出来供检索。
"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb"
d = open(P, "rb").read()
info = pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl", "rb"))
BS = info["BS"]; sizes = info["sizes"]; blocks = info["blocks"]


def stream(i):
    return b"".join(d[b * BS:(b + 1) * BS] for b in blocks[i])[:sizes[i]]


s3 = stream(3)
u32 = lambda o: struct.unpack("<I", s3[o:o + 4])[0]
u16 = lambda o: struct.unpack("<H", s3[o:o + 2])[0]
print("sig=0x%08X version=%d headerSize=%d age=%d" % (u32(0), u32(4), u32(8), u32(12)))
gsStream = u16(16)
pssStream = u16(18)
symStream = u16(20)
print("gsStream=%d pssStream=%d symStream=%d" % (gsStream, pssStream, symStream))

# 符号记录流
sym = stream(symStream)
print("symStream size =", len(sym))
print("sym head:", sym[:32].hex(" "))

# 扫描 S_* 记录：每条记录 u16 len, u16 type, payload
records = []
off = 0
n = len(sym)
kinds = {}
while off + 4 <= n:
    rlen = struct.unpack("<H", sym[off:off + 2])[0]
    if rlen < 2 or off + rlen > n:
        break
    rtype = struct.unpack("<H", sym[off + 2:off + 4])[0]
    kinds[rtype] = kinds.get(rtype, 0) + 1
    records.append((off, rlen, rtype, sym[off + 4:off + rlen]))
    off += rlen
    # 记录按 4 字节对齐
    if rlen % 4:
        off += 4 - (rlen % 4)
print("records found:", len(records))
print("type histogram (top):", sorted(kinds.items(), key=lambda x: -x[1])[:12])

# S_PUB32=0x110E, S_GPROC32=0x1108, S_LPROC32=0x110A
targets = {0x110E: "PUB32", 0x1108: "GPROC32", 0x110A: "LPROC32", 0x1107: "OBJNAME", 0x1101: "COMPILE"}
hits = []
for off, rlen, rtype, payload in records:
    if rtype in targets:
        nm = payload.split(b"\x00")[0]
        hits.append((rtype, off, nm))
print("procedure symbols:", len(hits))
with open(r"F:\sr2-cn\_pdb_syms.txt", "w", encoding="utf-8") as f:
    for rtype, off, nm in hits:
        f.write("%s %s\n" % (targets[rtype], nm.decode("ascii", "replace")))
print("saved _pdb_syms.txt")
# 打印含 MStrings / LoadChar / font 的
import re
for kw in [b"MStrings", b"harList", b"harList", b"loadchar", b"LoadChar", b"font", b"Font", b"Glyph", b"glyph", b"vint", b"Vint"]:
    c = 0
    for rtype, off, nm in hits:
        if kw in nm:
            if c < 20:
                print("  %-10s off=0x%-8X %s" % (targets[rtype], off, nm.decode("ascii", "replace")))
            c += 1
    print("  [%s] total %d" % (kw.decode(), c))
