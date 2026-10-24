# -*- coding: utf-8 -*-
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
d = open(r"F:/sr2-cn/SR2_pc.exe.orig", "rb").read()
A, B = 10358560, 10359120
print("=== hex %d..%d ===" % (A, B))
for off in range(A, B, 16):
    chunk = d[off:off+16]
    print("%8d  %-47s  %s" % (off, " ".join("%02X" % c for c in chunk),
          "".join(chr(c) if 32 <= c < 127 else "." for c in chunk)))
print("\n=== 视为 u32 数组 ===")
for off in range(A, B, 4):
    v = struct.unpack_from("<I", d, off)[0]
    print("%8d  %10d  0x%08X" % (off, v, v))
