# -*- coding: utf-8 -*-
"""对比自制 PE 与真实 PE 的头部差异。"""
import struct
import sys

FIELDS_OPT = [
    (0, "H", "Magic"),
    (2, "B", "MajorLinkerVersion"),
    (3, "B", "MinorLinkerVersion"),
    (4, "I", "SizeOfCode"),
    (8, "I", "SizeOfInitializedData"),
    (12, "I", "SizeOfUninitializedData"),
    (16, "I", "AddressOfEntryPoint"),
    (20, "I", "BaseOfCode"),
    (24, "I", "BaseOfData"),
    (28, "I", "ImageBase"),
    (32, "I", "SectionAlignment"),
    (36, "I", "FileAlignment"),
    (40, "H", "MajorOperatingSystemVersion"),
    (42, "H", "MinorOperatingSystemVersion"),
    (44, "H", "MajorImageVersion"),
    (46, "H", "MinorImageVersion"),
    (48, "H", "MajorSubsystemVersion"),
    (50, "H", "MinorSubsystemVersion"),
    (52, "I", "Win32VersionValue"),
    (56, "I", "SizeOfImage"),
    (60, "I", "SizeOfHeaders"),
    (64, "I", "CheckSum"),
    (68, "H", "Subsystem"),
    (70, "H", "DllCharacteristics"),
    (72, "I", "SizeOfStackReserve"),
    (76, "I", "SizeOfStackCommit"),
    (80, "I", "SizeOfHeapReserve"),
    (84, "I", "SizeOfHeapCommit"),
    (88, "I", "LoaderFlags"),
    (92, "I", "NumberOfRvaAndSizes"),
]


def dump(path, label):
    d = open(path, "rb").read()
    print("=" * 74)
    print("%s  (%s, %d 字节)" % (label, path, len(d)))
    print("=" * 74)
    if d[:2] != b"MZ":
        print("  ★ 不是 MZ")
        return
    e = struct.unpack_from("<I", d, 0x3C)[0]
    print("  e_lfanew = 0x%X" % e)
    if d[e:e + 4] != b"PE\x00\x00":
        print("  ★ PE 签名错误: %r" % d[e:e + 4])
        return
    mach, nsec, tds, psym, nsym, optsz, chars = struct.unpack_from("<HHIIIHH", d, e + 4)
    print("  COFF: Machine=0x%04X Sections=%d TimeDate=0x%X PtrSym=0x%X NumSym=%d OptSize=%d Chars=0x%04X"
          % (mach, nsec, tds, psym, nsym, optsz, chars))
    opt = e + 24
    magic, = struct.unpack_from("<H", d, opt)
    print("  Optional: Magic=0x%X" % magic)
    for off, fmt, name in FIELDS_OPT:
        if off >= optsz:
            break
        v, = struct.unpack_from("<" + fmt, d, opt + off)
        if name in ("Magic", "MajorLinkerVersion", "MinorLinkerVersion"):
            continue
        print("    +0x%02X %-30s = 0x%X (%d)" % (off, name, v, v))
    # 数据目录
    print("  DataDirectory:")
    for i in range(min(16, (optsz - 96) // 8)):
        rva, sz = struct.unpack_from("<II", d, opt + 96 + i * 8)
        if rva or sz:
            print("    [%2d] RVA=0x%-8X size=%d" % (i, rva, sz))
    # 节表
    print("  节表 @ 0x%X:" % (opt + optsz))
    for i in range(nsec):
        o = opt + optsz + i * 40
        nm = d[o:o + 8].rstrip(b"\x00").decode("latin1")
        vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", d, o + 8)
        print("    %-10s VSize=0x%-6X VA=0x%-6X RSize=0x%-6X RP=0x%-6X RelP=0x%-6X LnP=0x%-6X nRel=%-4d nLn=%-4d Flags=0x%08X"
              % (nm, vs, va, rs, rp, relp, lnp, nrel, nln, fl))
    print()


dump(r"F:\sr2-cn\asi\loadtest.exe", "自制 EXE")
dump(r"C:\Windows\SysWOW64\regsvr32.exe", "真实 EXE")
dump(r"F:\sr2-cn\asi\dinput8.dll", "自制 DLL")
