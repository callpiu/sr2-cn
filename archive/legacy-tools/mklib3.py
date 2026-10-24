# -*- coding: utf-8 -*-
"""生成 COFF 导入库（.lib）—— 完整支持长符号名。

ar 归档结构
    "!<arch>\\n"
    "/"   符号索引成员
           NumberOfSymbols(4)
           [ Offset(4) + Name(8) ] * n      ← MSVC 风格：名称全部 8 字节
    "//"  长名称表成员（当索引名需要完整名时使用）
    对象成员

关键点（之前一直失败的原因）
    Windows 链接器读归档符号索引时，名称字段固定 8 字节。
    若符号名超过 8 字节，必须：
      a) 在 "//" 成员里放完整名称
      b) 索引项写 "/<十进制偏移>"
    仅截断前 8 字节会导致 lld-link 匹配不到。

用法
    python mklib3.py out.lib dllname Func1:argbytes ...
"""
import struct
import sys

MACHINE_I386 = 0x014C
SYM_CLASS_EXTERNAL = 2
SYM_DTYPE_FUNCTION = 0x20


def make_idata_sec(dll, func):
    fn = func.encode() + b"\x00"
    dllb = dll.encode() + b"\x00"
    hint_name = struct.pack("<H", 0) + fn
    off_hintname = 36
    off_dll = off_hintname + len(hint_name)
    if off_dll % 2:
        hint_name += b"\x00"
        off_dll += 1
    sec = bytearray(off_dll + len(dllb))
    struct.pack_into("<I", sec, 0, off_hintname)
    struct.pack_into("<I", sec, 12, off_dll)
    struct.pack_into("<I", sec, 16, off_hintname)
    struct.pack_into("<I", sec, 20, off_hintname)
    struct.pack_into("<I", sec, 28, off_hintname)
    sec[off_hintname:off_hintname + len(hint_name)] = hint_name
    sec[off_dll:off_dll + len(dllb)] = dllb
    return bytes(sec)


def make_coff(dll, func, nargs):
    """构造 COFF 对象成员，返回 (obj_bytes, [符号名...])。"""
    decorated = ("_%s@%d" % (func, nargs)) if nargs else func
    imp_name = "__imp_" + decorated
    sec = make_idata_sec(dll, func)
    strtab = bytearray()

    def sym_entry(name, strtab=strtab):
        e = bytearray(18)
        nb = name.encode()
        if len(nb) <= 8:
            e[0:len(nb)] = nb
        else:
            off = len(strtab)
            strtab += nb + b"\x00"
            struct.pack_into("<I", e, 0, 0)
            struct.pack_into("<I", e, 4, off)
        struct.pack_into("<I", e, 8, 0)
        struct.pack_into("<h", e, 12, 1)
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
    struct.pack_into("<I", body, 8, symoff)
    struct.pack_into("<I", body, 12, 2)

    # 附上字符串表（大小 + 名称）
    st = struct.pack("<I", len(strtab) + 4) + bytes(strtab)
    return bytes(body) + st, [imp_name, decorated]


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
    symbols = []      # (完整名, 成员索引)
    for i, spec in enumerate(funcs):
        parts = spec.rsplit(":", 1)
        if len(parts) == 2 and parts[1].isdigit():
            fname, nargs = parts[0], int(parts[1])
        else:
            fname, nargs = spec, 0
        c, syms = make_coff(dll, fname, nargs)
        coffs.append(c)
        for s in syms:
            symbols.append((s, i))

    n = len(symbols)

    # ---- 长名称表 "//" ----
    longnames = bytearray()
    long_off = {}
    for name, _ in symbols:
        if len(name) > 8:
            long_off[name] = len(longnames)
            longnames += name.encode() + b"\n"      # ar 长名以 \n 结尾
    has_long = len(longnames) > 0
    if has_long and len(longnames) % 2:
        longnames += b"\n"

    # ---- 符号索引 "/" ----
    # 布局: magic(8) + / (60+size) + // (60+size，可选) + 对象...
    idx_size = 4 + n * 12 + 4
    pos = 8
    pos += 60 + idx_size
    if idx_size % 2:
        pos += 1
    long_member_off = None
    if has_long:
        long_member_off = pos
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
            # "/<offset>" 形式
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
    print("✓ %s: %d 字节 (%d 符号, 长名表 %d 字节)" %
          (out, len(out_data), n, len(longnames)))
    for name, mi in symbols:
        tag = " (长名)" if len(name) > 8 else ""
        print("    %-34s 成员 #%d @%d%s" % (name, mi, member_offsets[mi], tag))


if __name__ == "__main__":
    build(sys.argv[2], sys.argv[3:], sys.argv[1])
