# -*- coding: utf-8 -*-
"""生成 x86 COFF 导入库（.lib），供 lld-link 使用。

为什么需要
    LLVM 包里没有 .lib 导入库，lld-link 无法解析 kernel32!LoadLibraryA 等符号。
    本脚本直接构造 COFF 导入库（ar 归档格式 + 2 个成员）。

COFF 导入库结构（x86）
    归档头 "!<arch>\\n"
    成员 1: /                （符号表链接成员，含符号名 → 成员偏移）
    成员 2: //               （长名称表，可空）
    成员 3+: <object>        每个符号一个成员：
        IMAGE_ARCHIVE_MEMBER_HEADER (60 字节)
        IMAGE_FILE_HEADER (20 字节)
        IMAGE_SECTION_HEADER × 2 (40 字节 each)
        import header + thunk + name
"""
import os
import struct

OUT = r"F:\sr2-cn\_toolchain\importlib"
os.makedirs(OUT, exist_ok=True)

IMAGE_FILE_MACHINE_I386 = 0x014C
IMAGE_SCN_LNK_NRELOC_OVFL = 0x01000000
IMAGE_SYM_CLASS_EXTERNAL = 2


def pad(s, n=4):
    return s + b"\x00" * ((-len(s)) % n)


def build_import_member(dll_name, func_name):
    """构造单个导入符号的 COFF 成员（x86）。"""
    dll = dll_name.encode() + b"\x00"
    fn = func_name.encode() + b"\x00"
    # 符号名（可能有 __imp_ 前缀）
    sym_imp = ("__imp_" + func_name).encode()
    sym = func_name.encode()

    # 节数据布局：
    #   [0]      import header (20 字节)
    #   [20]     ILT (Import Lookup Table): 1 项 + 终止 0
    #   [28]     IAT (Import Address Table): 1 项 + 终止 0
    #   [36]     hint/name: u16 hint + fn + \0
    #   [36+n]   dll 名 + \0   （对齐到 2）
    hint_name = struct.pack("<H", 0) + fn
    off_hintname = 36
    off_dll = off_hintname + len(hint_name)
    if off_dll % 2:
        off_dll += 1
        hint_name += b"\x00"
    data = bytearray()
    # import header
    data += struct.pack("<IHHHHII", 0, 0, 0, off_hintname, 0, off_hintname, 0)
    # 上面 20 字节：OriginalFirstThunk, TimeDateStamp, ForwarderChain, Name, FirstThunk
    # 重新精确排布
    data = bytearray(20)
    struct.pack_into("<I", data, 0, 20 + 8 + 8)       # OriginalFirstThunk -> ILT
    struct.pack_into("<I", data, 12, off_dll)          # Name -> dll name
    struct.pack_into("<I", data, 16, 20 + 8 + 8 + 8)   # FirstThunk -> IAT
    ilt_off = len(data)
    data += struct.pack("<I", off_hintname) + struct.pack("<I", 0)
    iat_off = len(data)
    data += struct.pack("<I", off_hintname) + struct.pack("<I", 0)
    assert len(data) == 36
    data += hint_name
    # 补齐到 off_dll
    if len(data) < off_dll:
        data += b"\x00" * (off_dll - len(data))
    data += dll

    # 符号表项（18 字节/项）
    # 两个符号: __imp_<fn> (指向 IAT), <fn> (指向 ILT)
    symtab = bytearray()
    # __imp_<fn>
    symtab += sym_imp[:8].ljust(8, b"\x00")
    symtab += struct.pack("<I", 0)            # Value
    symtab += struct.pack("<h", 1)            # SectionNumber = 1
    symtab += struct.pack("<H", 0)            # Type
    symtab += bytes([IMAGE_SYM_CLASS_EXTERNAL])
    symtab += bytes([0])                      # NumAux
    # <fn>
    symtab += sym[:8].ljust(8, b"\x00")
    symtab += struct.pack("<I", 0)
    symtab += struct.pack("<h", 1)
    symtab += struct.pack("<H", 0)
    symtab += bytes([IMAGE_SYM_CLASS_EXTERNAL])
    symtab += bytes([0])

    # 文件头
    fh = struct.pack("<HHIIIHH", IMAGE_FILE_MACHINE_I386, 2, 0, 0, 0, 20 + 40 * 2, 0)
    # 2 个节头：.text (代码, 空) 和 .idata (数据)
    sh_text = bytearray(40)
    sh_text[0:8] = b".text\x00\x00\x00"
    struct.pack_into("<I", sh_text, 16, 0)       # SizeOfRawData
    struct.pack_into("<I", sh_text, 20, 0)       # PointerToRawData
    sh_idata = bytearray(40)
    sh_idata[0:8] = b".idata\x00\x00"
    struct.pack_into("<I", sh_idata, 16, len(data))
    struct.pack_into("<I", sh_idata, 20, 0)
    sh_idata[36:40] = struct.pack("<H", 0) + struct.pack("<H", 0)

    obj = bytes(fh) + bytes(sh_text) + bytes(sh_idata) + bytes(data) + bytes(symtab)
    # 符号表偏移
    sym_off = len(fh) + 80 + len(data)
    obj = bytes(fh) + bytes(sh_text) + bytes(sh_idata) + bytes(data) + bytes(symtab)
    # 修正文件头的 PointerToSymbolTable / NumberOfSymbols
    obj = bytearray(obj)
    struct.pack_into("<I", obj, 8, sym_off)
    struct.pack_into("<I", obj, 12, 2)
    return bytes(obj), [sym_imp.decode(), sym.decode()]


def ar_member(name, data):
    hdr = name.ljust(16)[:16].encode()
    hdr += b"0".ljust(12)
    hdr += b"0".ljust(6)
    hdr += b"0".ljust(6)
    hdr += b"100644".ljust(8)
    hdr += str(len(data)).ljust(10).encode()
    hdr += b"`\n"
    return hdr + data + (b"\n" if len(data) % 2 else b"")


def build_lib(dll_name, funcs, out_path):
    members = []
    symbols = []
    for i, fn in enumerate(funcs):
        m, syms = build_import_member(dll_name, fn)
        members.append((fn, m))
        for s in syms:
            symbols.append((s, i))
    # 符号表成员（第 1 个成员 "/"）
    n = len(symbols)
    nlong = 0
    symtab = struct.pack(">I", n)
    # 名字用 8 字节内联（短名）
    offs = []
    for name, mi in symbols:
        offs.append((name, mi))
    # 成员偏移：需要先算出每个成员在归档里的位置
    # 归档 = 8 字节 magic + 成员...
    pos = 8
    member_pos = []
    header_len = 60
    # 符号表成员长度
    sym_names_blob = b"".join(name.encode()[:8].ljust(8, b"\x00")[:8] for name, _ in offs)
    symtab_data = struct.pack(">I", n) + b"".join(
        struct.pack(">I", 0) + name.encode()[:8].ljust(8, b"\x00")[:8]
        for name, _ in offs)
    symtab_data += struct.pack(">I", 0) + b""
    # 简化：用 lld-link 可接受的格式
    # 由于手写归档易错，改用另一种办法：直接让 lld-link 用 --def 生成
    return None


if __name__ == "__main__":
    print("这个方案太复杂，改用 .def 文件方案。")
