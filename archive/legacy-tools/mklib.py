# -*- coding: utf-8 -*-
"""生成 COFF 导入库（.lib），格式符合 Microsoft 规范，供 lld-link 使用。

COFF 导入库结构 = ar 归档，成员依次为：
    /              符号表成员（符号名 -> 成员偏移）
    //             长名称表（本实现不需要）
    <member>       每个导入符号一个成员：
                     IMAGE_ARCHIVE_MEMBER_HEADER (60 B)
                     IMAGE_FILE_HEADER (20 B)
                     IMAGE_SECTION_HEADER[2] (80 B)
                     import header + ILT + IAT + hint/name + dllname
                     COFF 符号表（2 项: __imp_X 和 X）

用法
    python mklib.py kernel32.lib LoadLibraryA GetProcAddress ...
"""
import os
import struct
import sys

IMAGE_FILE_MACHINE_I386 = 0x014C
IMAGE_SYM_CLASS_EXTERNAL = 2
IMAGE_SYM_DTYPE_FUNCTION = 0x20


def align_up(n, a):
    return (n + a - 1) & ~(a - 1)


def make_member(dll, func, nargs=0):
    """构造单个导入符号的 COFF 目标成员。

    x86 stdcall 需要修饰名: _Func@N
    nargs = 参数字节数（如 LoadLibraryA 有 1 个 4 字节参数 -> @4）
    """
    fn = func.encode() + b"\x00"
    dllb = dll.encode() + b"\x00"
    if nargs:
        decorated = "_%s@%d" % (func, nargs)
    else:
        decorated = func

    # 节数据（.idata）
    hint_name = struct.pack("<H", 0) + fn
    off_hintname = 20 + 8 + 8          # header + ILT(2 entries) + IAT(2 entries)
    off_dll = off_hintname + len(hint_name)
    if off_dll % 2:
        hint_name += b"\x00"
        off_dll += 1

    sec_data = bytearray(off_dll + len(dllb))
    # import header
    struct.pack_into("<I", sec_data, 0, off_hintname)      # OriginalFirstThunk (RVA)
    struct.pack_into("<I", sec_data, 4, 0)                 # TimeDateStamp
    struct.pack_into("<I", sec_data, 8, 0)                 # ForwarderChain
    struct.pack_into("<I", sec_data, 12, off_dll)          # Name (RVA)
    struct.pack_into("<I", sec_data, 16, off_hintname)     # FirstThunk (RVA)
    # ILT
    struct.pack_into("<I", sec_data, 20, off_hintname)
    struct.pack_into("<I", sec_data, 24, 0)
    # IAT
    struct.pack_into("<I", sec_data, 28, off_hintname)
    struct.pack_into("<I", sec_data, 32, 0)
    # hint/name + dll name
    sec_data[off_hintname:off_hintname + len(hint_name)] = hint_name
    sec_data[off_dll:off_dll + len(dllb)] = dllb

    # 符号表（2 项，各 18 字节）
    sym_imp = ("__imp_" + decorated).encode()[:8].ljust(8, b"\x00")
    sym_fn = decorated.encode()[:8].ljust(8, b"\x00")
    _ = sym_imp, sym_fn
    symtab = bytearray()
    symtab += sym_imp
    symtab += struct.pack("<IhHBB", 0, 1, IMAGE_SYM_DTYPE_FUNCTION, IMAGE_SYM_CLASS_EXTERNAL, 0)
    symtab += sym_fn
    symtab += struct.pack("<IhHBB", 0, 1, IMAGE_SYM_DTYPE_FUNCTION, IMAGE_SYM_CLASS_EXTERNAL, 0)

    # 文件头
    fh = struct.pack("<HHIIIHH", IMAGE_FILE_MACHINE_I386, 2, 0, 0, 0, 20 + 80, 2)
    # 节头 1: .text（空）
    sh1 = bytearray(40)
    sh1[0:8] = b".text\x00\x00\x00"
    struct.pack_into("<I", sh1, 16, 0)     # SizeOfRawData
    struct.pack_into("<I", sh1, 20, 0)     # PointerToRawData
    struct.pack_into("<I", sh1, 36, 0x60500020)
    # 节头 2: .idata
    sh2 = bytearray(40)
    sh2[0:8] = b".idata\x00\x00"
    struct.pack_into("<I", sh2, 8, 0)      # VirtualSize
    struct.pack_into("<I", sh2, 12, 0)     # VirtualAddress
    struct.pack_into("<I", sh2, 16, 0)     # SizeOfRawData（导入库模板里为 0）
    struct.pack_into("<I", sh2, 20, 0)     # PointerToRawData
    struct.pack_into("<I", sh2, 36, 0xC0300040)

    body = bytes(fh) + bytes(sh1) + bytes(sh2) + bytes(sec_data) + bytes(symtab)
    symoff = 20 + 80 + len(sec_data)
    body = bytearray(body)
    struct.pack_into("<I", body, 8, symoff)    # PointerToSymbolTable
    struct.pack_into("<I", body, 12, 2)        # NumberOfSymbols
    return bytes(body), ["__imp_" + decorated, decorated]


def ar_header(name, size):
    """ar 头部：每个字段必须用空格右填充到固定宽度（不能用零填充左侧）。"""
    h = name[:16].ljust(16, b" ") if isinstance(name, bytes) else name.encode()[:16].ljust(16, b" ")
    h += b"0".ljust(12, b" ")        # date
    h += b"0".ljust(6, b" ")         # uid
    h += b"0".ljust(6, b" ")         # gid
    h += b"100666".ljust(8, b" ")    # mode
    h += str(size).encode().ljust(10, b" ")
    h += b"`\n"
    assert len(h) == 60, len(h)
    return h


def build(dll, funcs, out):
    members = []
    symbols = []           # (name, member_index)
    for i, f in enumerate(funcs):
        if ":" in f:
            nm, na = f.split(":")
            m, syms = make_member(dll, nm, int(na))
        else:
            m, syms = make_member(dll, f, 0)
        members.append(m)
        for s in syms:
            symbols.append((s, i))

    # 计算各成员在归档中的偏移（magic 8 字节 + 每成员 60 字节头）
    # 归档布局: 8 + [60 + len(m0)] + [60 + len(m1)] + ...
    # 符号表成员 / 在最前，其大小 = 4 + n*4 + n*8? 实际格式：
    #   NumberOfSymbols(4) + [Offset(4) + Name(8)] * n + [StringTable]
    n = len(symbols)
    symtab_size = 4 + n * 12 + 4
    # 成员偏移
    offsets = []
    pos = 8 + 60 + symtab_size      # 跳过 magic + / 成员（含头）
    pos = align_up(pos, 2)
    for m in members:
        offsets.append(pos)
        pos += 60 + len(m)
        pos = align_up(pos, 2)

    # 构造 / 成员
    st = struct.pack(">I", n)
    for name, mi in symbols:
        st += struct.pack(">I", offsets[mi])
        st += name.encode()[:8].ljust(8, b"\x00")[:8]
    st += b"\x00\x00\x00\x00"       # 空字符串表
    symtab_member = st

    out_data = bytearray(b"!<arch>\n")
    out_data += ar_header("/", len(symtab_member))
    out_data += symtab_member
    if len(symtab_member) % 2:
        out_data += b"\n"
    for i, m in enumerate(members):
        out_data += ar_header("/", len(m))
        out_data += m
        if len(m) % 2:
            out_data += b"\n"

    open(out, "wb").write(bytes(out_data))
    print("✓ %s: %d 字节, %d 个符号" % (out, len(out_data), n))
    for name, mi in symbols:
        print("    %-34s 成员 #%d" % (name, mi))


if __name__ == "__main__":
    out = sys.argv[1]
    dll = sys.argv[2]
    funcs = sys.argv[3:]
    build(dll, funcs, out)
