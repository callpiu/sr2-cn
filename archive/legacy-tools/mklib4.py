# -*- coding: utf-8 -*-
"""生成 COFF 导入库 —— 使用【未修饰】符号名（MSVC 风格）。

关键
    MSVC 官方的 kernel32.lib 里，符号名是未修饰的:
        LoadLibraryA, ExitProcess, ...
    而编译器生成的引用是修饰的:
        _LoadLibraryA@4, __imp__LoadLibraryA@4
    链接器内部会做修饰名 -> 未修饰名的匹配。

    所以导入库成员里的 COFF 符号表必须写【未修饰名】。

用法
    python mklib4.py out.lib dllname Func1 Func2 ...
"""
import struct
import sys

MACHINE_I386 = 0x014C
SYM_CLASS_EXTERNAL = 2
SYM_DTYPE_FUNCTION = 0x20


def make_coff(dll, func):
    fn = func.encode() + b"\x00"
    dllb = dll.encode() + b"\x00"

    hint_name = struct.pack("<H", 0) + fn
    off_hintname = 36
    off_dll = off_hintname + len(hint_name)
    if off_dll % 2:
        hint_name += b"\x00"
        off_dll += 1

    sec = bytearray(off_dll + len(dllb))
    struct.pack_into("<I", sec, 0, off_hintname)     # OriginalFirstThunk
    struct.pack_into("<I", sec, 12, off_dll)         # Name
    struct.pack_into("<I", sec, 16, off_hintname)    # FirstThunk
    struct.pack_into("<I", sec, 20, off_hintname)    # ILT[0]
    struct.pack_into("<I", sec, 28, off_hintname)    # IAT[0]
    sec[off_hintname:off_hintname + len(hint_name)] = hint_name
    sec[off_dll:off_dll + len(dllb)] = dllb

    # 符号表：用【未修饰】名
    def sym_entry(name, strtab):
        e = bytearray(18)
        nb = name.encode()
        if len(nb) <= 8:
            e[0:len(nb)] = nb
        else:
            off = len(strtab)
            strtab += nb + b"\x00"
            struct.pack_into("<I", e, 0, 0)
            struct.pack_into("<I", e, 4, off)
        struct.pack_into("<I", e, 8, 0)          # Value = 0
        struct.pack_into("<h", e, 12, 1)         # SectionNumber
        struct.pack_into("<H", e, 14, SYM_DTYPE_FUNCTION)
        e[16] = SYM_CLASS_EXTERNAL
        e[17] = 0
        return bytes(e)

    strtab = bytearray()
    imp_name = "__imp_" + func
    symtab = sym_entry(imp_name, strtab) + sym_entry(func, strtab)

    fh = struct.pack("<HHIIIHH", MACHINE_I386, 2, 0, 0, 0, 20 + 80, 2)
    sh1 = bytearray(40)
    sh1[0:8] = b".text\x00\x00\x00"
    struct.pack_into("<I", sh1, 36, 0x60500020)
    sh2 = bytearray(40)
    sh2[0:8] = b".idata\x00\x00"
    struct.pack_into("<I", sh2, 16, len(sec))
    struct.pack_into("<I", sh2, 36, 0xC0300040)

    body = bytearray(fh) + sh1 + sh2 + sec + symtab
    struct.pack_into("<I", body, 8, 20 + 80 + len(sec))    # PointerToSymbolTable
    struct.pack_into("<I", body, 12, 2)                    # NumberOfSymbols
    st = struct.pack("<I", len(strtab) + 4) + bytes(strtab)
    return bytes(body) + st, [imp_name, func]


def arhdr(name, size):
    h = name.encode()[:16].ljust(16, b" ")
    h += b"0".ljust(12, b" ")
    h += b"0".ljust(6, b" ")
    h += b"0".ljust(6, b" ")
    h += b"100666".ljust(8, b" ")
    h += str(size).encode().ljust(10, b" ")
    h += b"`\n"
    assert len(h) == 60
    return h


def build(dll, funcs, out):
    coffs = []
    symbols = []
    for i, f in enumerate(funcs):
        c, syms = make_coff(dll, f)
        coffs.append(c)
        for s in syms:
            symbols.append((s, i))

    n = len(symbols)
    longnames = bytearray()
    long_off = {}
    for name, _ in symbols:
        if len(name) > 8:
            long_off[name] = len(longnames)
            longnames += name.encode() + b"\n"
    has_long = len(longnames) > 0
    if has_long and len(longnames) % 2:
        longnames += b"\n"

    idx_size = 4 + n * 12 + 4
    pos = 8 + 60 + idx_size
    if idx_size % 2:
        pos += 1
    if has_long:
        pos += 60 + len(longnames)
        if len(longnames) % 2:
            pos += 1

    member_offsets = []
    for c in coffs:
        member_offsets.append(pos)
        pos += 60 + len(c)
        if len(c) % 2:
            pos += 1

    idx = struct.pack(">I", n)
    for name, mi in symbols:
        if len(name) > 8 and has_long:
            ref = ("/%d" % long_off[name]).encode()
            idx += struct.pack(">I", member_offsets[mi]) + ref.ljust(8, b"\x00")[:8]
        else:
            idx += struct.pack(">I", member_offsets[mi]) + name.encode().ljust(8, b"\x00")[:8]
    idx += b"\x00\x00\x00\x00"

    out_data = bytearray(b"!<arch>\n")
    out_data += arhdr("/", len(idx))
    out_data += idx
    if len(idx) % 2:
        out_data += b"\n"
    if has_long:
        out_data += arhdr("//", len(longnames))
        out_data += longnames
        if len(longnames) % 2:
            out_data += b"\n"
    for c in coffs:
        out_data += arhdr("/", len(c))
        out_data += c
        if len(c) % 2:
            out_data += b"\n"

    open(out, "wb").write(bytes(out_data))
    print("✓ %s: %d 字节 (%d 符号)" % (out, len(out_data), n))
    for name, mi in symbols:
        print("    %-30s 成员 #%d" % (name, mi))


if __name__ == "__main__":
    build(sys.argv[2], sys.argv[3:], sys.argv[1])
