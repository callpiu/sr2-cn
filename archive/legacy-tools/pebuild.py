# -*- coding: utf-8 -*-
"""PE32 (x86) DLL 生成器：把 clang 编译出的 .obj 机器码 + 手写导入表，组装成 DLL。

为什么这么做
    LLVM 包里没有 .lib 导入库，lld-link 无法解析 kernel32 符号。
    而我们的 DLL 只需要少量 kernel32 API，完全可以手工构造导入表。

输入
    一个 .obj（clang -c 产出），其中只有 .text（代码）和可能的重定位。
    为简化：要求代码【不引用外部数据符号】（只用 import 的函数）。

输出
    合法的 PE32 DLL，导入表含：
        kernel32.dll: LoadLibraryA, GetProcAddress, DisableThreadLibraryCalls,
                      OutputDebugStringA, VirtualAlloc, VirtualProtect
"""
import os
import struct
import sys

# ---------------------------------------------------------------- COFF 解析
def parse_coff(data):
    """解析 COFF obj，返回 sections 和 symbols。"""
    machine, nsec, tds, symoff, nsym, optsz, chars = struct.unpack_from("<HHIIIHH", data, 0)
    assert machine == 0x014C, "不是 x86 COFF (machine=0x%04X)" % machine
    secs = []
    for i in range(nsec):
        o = 20 + optsz + i * 40
        name = data[o:o + 8].rstrip(b"\x00").decode("latin1")
        vsize, vaddr, rawsize, rawptr, relptr, lnptr, nrel, nln, flags = struct.unpack_from("<IIIIIIHHI", data, o + 8)
        secs.append(dict(name=name, vsize=vsize, rawsize=rawsize, rawptr=rawptr,
                         relptr=relptr, nrel=nrel, flags=flags))
    syms = []
    for i in range(nsym):
        o = symoff + i * 18
        nm = data[o:o + 8]
        val, secnum, typ, cls, naux = struct.unpack_from("<IhHBB", data, o + 8)
        if nm[:4] == b"\x00\x00\x00\x00":
            stroff = struct.unpack_from("<I", nm, 4)[0]
            end = data.index(b"\x00", stroff)
            name = data[stroff:end].decode("latin1")
        else:
            name = nm.rstrip(b"\x00").decode("latin1")
        syms.append(dict(name=name, value=val, sec=secnum, type=typ, cls=cls, naux=naux, off=o))
    return secs, syms


def main(obj_path, out_path, imports):
    data = open(obj_path, "rb").read()
    secs, syms = parse_coff(data)
    print("COFF: %d 节, %d 符号" % (len(secs), len(syms)))
    for s in secs:
        print("  %-10s rawsize=%-6d relocs=%-4d flags=0x%08X" % (s["name"], s["rawsize"], s["nrel"], s["flags"]))
    # 打印未定义符号（需要导入的）
    undef = [s["name"] for s in syms if s["sec"] == 0]
    print("  未定义符号（需导入）: %s" % undef)
    print()
    # 收集重定位
    all_rel = []
    for s in secs:
        if s["nrel"] == 0:
            continue
        for i in range(s["nrel"]):
            o = s["relptr"] + i * 10
            va, symidx, typ = struct.unpack_from("<IIH", data, o)
            all_rel.append((s["name"], va, symidx, typ))
    print("  重定位 %d 个" % len(all_rel))
    for sn, va, si, ty in all_rel[:20]:
        nm = syms[si]["name"] if si < len(syms) else "?"
        print("    %s + 0x%X -> %s (type %d)" % (sn, va, nm, ty))
    return


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None, None)
