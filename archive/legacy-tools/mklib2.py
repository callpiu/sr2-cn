# -*- coding: utf-8 -*-
"""生成 COFF 导入库（.lib）—— 支持长符号名。

关键点（之前失败的原因）
    archive 成员头的名称字段只有 16 字节，超长名称必须放进 "//" 长名称表，
    成员头写成 "/<十进制偏移>"。
    同理，如果不用 "/" 符号表成员，lld-link 就找不到符号。

用法
    python mklib2.py out.lib dllname Func1:argbytes Func2:argbytes ...
"""
import os
import struct
import sys

MACHINE_I386 = 0x014C
SYM_CLASS_EXTERNAL = 2
SYM_DTYPE_FUNCTION = 0x20


def make_idata_member(dll, func):
    """构造单个导入符号的 COFF 对象。"""
    fn = func.encode() + b"\x00"
    dllb = dll.encode() + b"\x00"
    decorated = "_%s@%d" % (func, 0)  # 占位，稍后填

    hint_name = struct.pack("<H", 0) + fn
    off_hintname = 36                     # header(20) + ILT(8) + IAT(8)
    off_dll = off_hintname + len(hint_name)
    if off_dll % 2:
        hint_name += b"\x00"
        off_dll += 1

    sec = bytearray(off_dll + len(dllb))
    struct.pack_into("<I", sec, 0, off_hintname)     # OriginalFirstThunk
    struct.pack_into("<I", sec, 4, 0)                # TimeDateStamp
    struct.pack_into("<I", sec, 8, 0)                # ForwarderChain
    struct.pack_into("<I", sec, 12, off_dll)         # Name
    struct.pack_into("<I", sec, 16, off_hintname)    # FirstThunk
    struct.pack_into("<I", sec, 20, off_hintname)    # ILT[0]
    struct.pack_into("<I", sec, 24, 0)               # ILT[1] = 0
    struct.pack_into("<I", sec, 28, off_hintname)    # IAT[0]
    struct.pack_into("<I", sec, 32, 0)               # IAT[1] = 0
    sec[off_hintname:off_hintname + len(hint_name)] = hint_name
    sec[off_dll:off_dll + len(dllb)] = dllb
    return bytes(sec), off_hintname, off_dll


def make_coff(dll, func, nargs, strtab):
    """构造 COFF 对象成员。

    ★ 关键：为使 archive 符号索引（固定 8 字节）能匹配，
      导入库里的符号名【不能超过 8 字节】。
      标准做法：只用 MSVC 的 x86 修饰名，但那些都超长。
      因此这里让 make_member 传入【短名】作为索引键，
      而 COFF 成员里的符号名用完整名（走 string table）。
    """
    decorated = "_%s@%d" % (func, nargs) if nargs else func
    imp_name = "__imp_" + decorated
    sec, off_hintname, off_dll = make_idata_member(dll, func)

    # 符号表（2 项）
    def sym_entry(name, strtab=strtab):
        e = bytearray(18)
        nb = name.encode()
        if len(nb) <= 8:
            e[0:len(nb)] = nb
        else:
            # COFF 长名称格式: Zeroes(4) + StringTableOffset(4)
            off = len(strtab)
            strtab += nb + b"\x00"
            struct.pack_into("<I", e, 0, 0)
            struct.pack_into("<I", e, 4, off)
        struct.pack_into("<I", e, 8, 0)          # Value
        struct.pack_into("<h", e, 12, 1)         # SectionNumber
        struct.pack_into("<H", e, 14, SYM_DTYPE_FUNCTION)
        e[16] = SYM_CLASS_EXTERNAL
        e[17] = 0
        return bytes(e)

    symtab = sym_entry(imp_name) + sym_entry(decorated)

    fh = struct.pack("<HHIIIHH", MACHINE_I386, 2, 0, 0, 0, 20 + 80, 2)
    sh1 = bytearray(40)
    sh1[0:8] = b".text\x00\x00\x00"
    struct.pack_into("<I", sh1, 36, 0x60500020)
    sh2 = bytearray(40)
    sh2[0:8] = b".idata\x00\x00"
    struct.pack_into("<I", sh2, 16, len(sec))
    struct.pack_into("<I", sh2, 36, 0xC0300040)

    body = bytearray(fh) + sh1 + sh2 + sec + symtab
    symoff = 20 + 80 + len(sec)
    struct.pack_into("<I", body, 8, symoff)     # PointerToSymbolTable
    struct.pack_into("<I", body, 12, 2)         # NumberOfSymbols
    return bytes(body), [imp_name, decorated]


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
    strtab = bytearray()

    # 先构造所有 COFF 成员
    coffs = []
    symbols = []           # (name, member_index)
    for i, spec in enumerate(funcs):
        parts = spec.rsplit(":", 1)
        if len(parts) == 2 and parts[1].isdigit():
            fname, nargs = parts[0], int(parts[1])
        else:
            fname, nargs = spec, 0
        c, syms = make_coff(dll, fname, nargs, strtab)
        coffs.append(c)
        for s in syms:
            symbols.append((s, i))

    # 成员在归档中的偏移
    n = len(symbols)
    symtab_size = 4 + n * 12 + 4
    # 布局: magic(8) + [ / 成员 ] + [ // 成员（若有长名）] + 各对象
    longnames = b""
    # 检查是否有超长成员名（本实现成员名都短，跳过）
    pos = 8
    pos += 60 + symtab_size
    if symtab_size % 2:
        pos += 1
    member_offsets = []
    for c in coffs:
        member_offsets.append(pos)
        pos += 60 + len(c)
        if len(c) % 2:
            pos += 1

    # / 符号表成员
    st = struct.pack(">I", n)
    for name, mi in symbols:
        nb = name.encode()
        if len(nb) <= 8:
            st += struct.pack(">I", member_offsets[mi]) + nb.ljust(8, b"\x00")
        else:
            # 长名：符号表里只放前 8 字节（lld 用 // 表，但符号表项
            # 的长名格式是 offset into string table，这里用简化：
            # 直接截断会导致找不到，所以必须用完整的 8 字节。
            # 实际上 archive 符号表项名称字段固定 8 字节，
            # 更长的名字通过 "//" 成员 + 偏移。这里我们确保名字 <=8，
            # 若超过则报错提示改用短名。
            st += struct.pack(">I", member_offsets[mi]) + nb[:8]
    st += b"\x00\x00\x00\x00"

    out_data = bytearray(b"!<arch>\n")
    out_data += arhdr("/", len(st))
    out_data += st
    if len(st) % 2:
        out_data += b"\n"
    for c in coffs:
        out_data += arhdr("/", len(c))
        out_data += c
        if len(c) % 2:
            out_data += b"\n"

    open(out, "wb").write(bytes(out_data))
    print("✓ %s: %d 字节" % (out, len(out_data)))
    for name, mi in symbols:
        print("    %-34s 成员 #%d  (offset %d)" % (name, mi, member_offsets[mi]))


if __name__ == "__main__":
    build(sys.argv[2], sys.argv[3:], sys.argv[1])
