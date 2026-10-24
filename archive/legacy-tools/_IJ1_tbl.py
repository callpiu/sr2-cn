# -*- coding: utf-8 -*-
# dump exe 里字体表区域
import struct
EXE = r"F:\sr2-cn\_backup_EXE\SR2_pc.exe.before_fontrename"
d = open(EXE, "rb").read()
IMAGE_BASE = 0x400000

def va2off(va):
    # .text VA=0x1000 Raw=0x1000  => off = va
    if 0x1000 <= va < 0x9b8000: return va
    if 0x9b8000 <= va < 0xa80000: return va
    return None

def cstr(va):
    o = va2off(va)
    if o is None: return "<bad>"
    e = d.find(b"\0", o)
    return d[o:e].decode("latin1", "replace")

def dump(start, end):
    print("=== file %#x .. %#x ===" % (start, end))
    o = start
    while o < end:
        row = d[o:o+16]
        hexs = " ".join("%02X" % b for b in row)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
        # 解释前 4/8 字节为指针
        p32 = struct.unpack_from("<I", d, o)[0]
        note = ""
        if 0x9b8000 <= p32 < 0xa80000:
            note = "  ->str@%#x = %r" % (p32, cstr(p32)[:40])
        elif 0x400000 <= p32 < 0x400000+0xa80000:
            note = "  ->va %#x" % (p32 - IMAGE_BASE)
        print("%08x  %-47s  %s%s" % (o, hexs, asc, note))
        o += 16

dump(0x11d240, 0x11d700)
