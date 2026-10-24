# -*- coding: utf-8 -*-
import re, struct
EXE = r"F:\sr2-cn\_backup_EXE\SR2_pc.exe.before_fontrename"
d = open(EXE, "rb").read()
IB = 0x400000

def dump(o0, o1, annot=True):
    print("=== file %#x .. %#x ===" % (o0, o1))
    o = o0
    while o < o1:
        row = d[o:o+16]
        note = ""
        if annot:
            p = struct.unpack_from("<I", d, o)[0]
            if IB + 0x9b8000 <= p < IB + 0xa80000:
                fo = p - IB
                e = d.find(b"\0", fo)
                s = d[fo:e]
                if 1 <= len(s) <= 40 and all(32 <= c < 127 for c in s):
                    note = "  -> %r" % s.decode()
        print("%08x  %-47s  %s%s" % (o, " ".join("%02X"%b for b in row),
              "".join(chr(b) if 32<=b<127 else "." for b in row), note))
        o += 16

dump(0xA25F00, 0xA26070)
