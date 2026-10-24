# -*- coding: utf-8 -*-
"""解析生成的 .lib，验证格式。"""
import struct
import sys

path = sys.argv[1] if len(sys.argv) > 1 else r"F:\sr2-cn\asi\kernel32.lib"
d = open(path, "rb").read()
print("文件 %s (%d 字节)" % (path, len(d)))
print("magic: %r" % d[:8])
assert d[:8] == b"!<arch>\n"

pos = 8
mi = 0
while pos + 60 <= len(d):
    hdr = d[pos:pos + 60]
    name = hdr[0:16].rstrip()
    size_s = hdr[48:58].rstrip()
    try:
        size = int(size_s)
    except ValueError:
        print("  [%d] @%d 头解析失败: %r" % (mi, pos, hdr))
        break
    data = d[pos + 60:pos + 60 + size]
    print("  [%d] @%-6d name=%-16r size=%d" % (mi, pos, name, size))
    if name == b"/":
        n, = struct.unpack_from(">I", data, 0)
        print("       符号数 = %d" % n)
        for i in range(n):
            off, = struct.unpack_from(">I", data, 4 + i * 12)
            nm = data[4 + i * 12 + 4:4 + i * 12 + 12]
            print("         %-34r -> 成员 @%d" % (nm, off))
    else:
        # 当作 COFF 对象解析
        if len(data) >= 20:
            mach, nsec, tds, psym, nsym, optsz, chars = struct.unpack_from("<HHIIIHH", data, 0)
            print("       COFF: machine=0x%04X nsec=%d nsym=%d pSym=0x%X optsz=%d" %
                  (mach, nsec, nsym, psym, optsz))
            for k in range(nsec):
                o = 20 + optsz + k * 40
                sn = data[o:o + 8].rstrip(b"\x00")
                vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", data, o + 8)
                print("         节 %-10r vs=%-5d rs=%-5d rp=%-5d nrel=%-3d flags=0x%08X" %
                      (sn, vs, rs, rp, nrel, fl))
            if nsym:
                print("         符号:")
                for k in range(min(nsym, 6)):
                    o = psym + k * 18
                    nm = data[o:o + 8]
                    val, secnum, typ, cls, naux = struct.unpack_from("<IhHBB", data, o + 8)
                    print("           %-28r val=%-5d sec=%-3d typ=0x%04X cls=%d" %
                          (nm, val, secnum, typ, cls))
    pos += 60 + size
    if size % 2:
        pos += 1
    mi += 1
    if mi > 12:
        break
