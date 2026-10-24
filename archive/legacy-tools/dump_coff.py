# -*- coding: utf-8 -*-
"""调试 COFF 符号与节名（长名 / 辅助记录）。"""
import sys
import struct

path = sys.argv[1]
data = open(path, "rb").read()
machine, nsec, tds, symoff, nsym, optsz, chars = struct.unpack_from("<HHIIIHH", data, 0)
strtab_off = symoff + nsym * 18
strtab_size, = struct.unpack_from("<I", data, strtab_off)
print("machine=0x%04X nsec=%d nsym=%d symoff=0x%X strtab=0x%X (size %d)" %
      (machine, nsec, nsym, symoff, strtab_off, strtab_size))
print()

# 节表（含长名）
print("=== 节表 ===")
for i in range(nsec):
    o = 20 + optsz + i * 40
    nm8 = data[o:o + 8]
    if nm8[:1] == b"/" and nm8[1:2].isdigit():
        so = int(nm8[1:].split(b"\x00")[0])
        p = strtab_off + so
        e = data.index(b"\x00", p)
        name = data[p:e].decode("latin1")
    else:
        name = nm8.rstrip(b"\x00").decode("latin1")
    vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", data, o + 8)
    print("  [%d] %-14s vs=%-6d rs=%-6d rp=0x%-6X nrel=%-3d flags=0x%08X" %
          (i + 1, name, vs, rs, rp, nrel, fl))
print()

# 字符串表内容
print("=== 字符串表（前 400 字节）===")
seg = data[strtab_off:strtab_off + min(400, strtab_size)]
parts = [p for p in seg.split(b"\x00") if p]
print("  %s" % " | ".join(p.decode("latin1", "replace") for p in parts[:40]))
print()

# 符号
print("=== 符号（前 90 个）===")
i = 0
n = 0
while i < nsym and n < 90:
    o = symoff + i * 18
    nm8 = data[o:o + 8]
    if nm8[:4] == b"\x00\x00\x00\x00":
        so = struct.unpack_from("<I", nm8, 4)[0]
        p = strtab_off + so
        e = data.index(b"\x00", p)
        name = data[p:e].decode("latin1")
    else:
        name = nm8.rstrip(b"\x00").decode("latin1")
    val, secnum, typ, cls, naux = struct.unpack_from("<IhHBB", data, o + 8)
    print("  #%-4d %-34s val=0x%-6X sec=%-4d cls=%-3d naux=%d" %
          (i, name[:34], val, secnum, cls, naux))
    i += 1 + naux
    n += 1
