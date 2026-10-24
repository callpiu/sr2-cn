# -*- coding: utf-8 -*-
"""COFF (.obj) -> PE32 (DLL) 最小链接器。

支持
    · 合并 .text / .rdata / .data / .bss / .CRT$XCU 等节
    · 应用 x86 重定位（IMAGE_REL_I386_DIR32 = 6, REL32 = 20）
    · 生成 PE32 头 + 节表 + 导出表
    · 零导入（代码用 PEB 自解析 kernel32）

限制
    · 只支持单 .obj
    · 不支持 /DELAYLOAD、TLS、异常表
    · 假设代码不引用需要导入的外部符号

用法
    python link_pe.py in.obj out.dll [--entry NAME]
"""
import os
import sys
import struct

IMAGE_FILE_MACHINE_I386 = 0x014C
IMAGE_REL_I386_ABSOLUTE = 0x0000
IMAGE_REL_I386_DIR32 = 0x0006
IMAGE_REL_I386_REL32 = 0x0014
IMAGE_SCN_MEM_EXECUTE = 0x20000000
IMAGE_SCN_MEM_READ = 0x40000000
IMAGE_SCN_MEM_WRITE = 0x80000000
IMAGE_SCN_CNT_CODE = 0x00000020
IMAGE_SCN_CNT_INITIALIZED_DATA = 0x00000040
IMAGE_SCN_CNT_UNINITIALIZED_DATA = 0x00000080


def parse_coff(data):
    machine, nsec, tds, symoff, nsym, optsz, chars = struct.unpack_from("<HHIIIHH", data, 0)
    if machine != IMAGE_FILE_MACHINE_I386:
        raise SystemExit("不是 x86 COFF (machine=0x%04X)" % machine)
    # 字符串表
    strtab_off = symoff + nsym * 18
    strtab_size, = struct.unpack_from("<I", data, strtab_off)

    def symname(o, nm8):
        if nm8[:4] == b"\x00\x00\x00\x00":
            so = struct.unpack_from("<I", nm8, 4)[0]
            p = strtab_off + so
            e = data.index(b"\x00", p)
            return data[p:e].decode("latin1")
        return nm8.rstrip(b"\x00").decode("latin1")

    syms = []
    i = 0
    while i < nsym:
        o = symoff + i * 18
        nm8 = data[o:o + 8]
        val, secnum, typ, cls, naux = struct.unpack_from("<IhHBB", data, o + 8)
        syms.append(dict(name=symname(o, nm8), value=val, sec=secnum,
                         type=typ, cls=cls, naux=naux, idx=i))
        i += 1 + naux

    secs = []
    for i in range(nsec):
        o = 20 + optsz + i * 40
        name = data[o:o + 8].rstrip(b"\x00").decode("latin1")
        vsize, vaddr, rawsize, rawptr, relptr, lnptr, nrel, nln, flags = \
            struct.unpack_from("<IIIIIIHHI", data, o + 8)
        rels = []
        for k in range(nrel):
            ro = relptr + k * 10
            va, si, ty = struct.unpack_from("<IIH", data, ro)
            rels.append(dict(va=va, sym=si, type=ty))
        if rawsize and rawptr:
            raw = data[rawptr:rawptr + rawsize]
        else:
            # .bss / 未初始化数据：用虚拟大小占位
            raw = b"\x00" * (vsize if vsize else 0)
        secs.append(dict(name=name, vsize=vsize, raw=bytearray(raw),
                         flags=flags, rels=rels, idx=i + 1))
    return secs, syms, strtab_off, nsym


SECMAP = {}

def merge_sections(secs):
    """按名字合并同名节（例如多个 .rdata）。返回 (merged, secmap)。"""
    out = {}
    order = []
    for s in secs:
        key = s["name"]
        if key not in out:
            out[key] = dict(name=key, data=bytearray(), flags=s["flags"], rels=[])
            order.append(key)
        base = len(out[key]["data"])
        # 对齐
        align = 16 if (s["flags"] & IMAGE_SCN_CNT_CODE) else 8
        pad = (-base) % align
        out[key]["data"] += b"\x00" * pad
        off = len(out[key]["data"])
        out[key]["data"] += s["raw"]
        out[key]["flags"] |= s["flags"]
        for r in s["rels"]:
            out[key]["rels"].append(dict(va=off + r["va"], sym=r["sym"],
                                         type=r["type"], sec_idx=s["idx"]))
        # 记录原节 -> (合并节名, 偏移)
        SECMAP[s["idx"]] = (key, off)
    return [out[k] for k in order], SECMAP


def build(obj_path, out_path, entry_name=None):
    data = open(obj_path, "rb").read()
    secs, syms, _, _ = parse_coff(data)
    merged, secmap = merge_sections(secs)
    print("合并后 %d 个节:" % len(merged))
    for s in merged:
        print("  %-12s %6d 字节  relocs=%d  flags=0x%08X" %
              (s["name"], len(s["data"]), len(s["rels"]), s["flags"]))

    # ---- 布局 ----
    # 每个节的 RVA：从 0x1000 开始，按 0x1000 对齐
    IMAGE_BASE = 0x10000000
    va = 0x1000
    for s in merged:
        s["rva"] = va
        va += (len(s["data"]) + 0xFFF) & ~0xFFF
    size_of_image = va

    # 文件偏移：节从 0x400 开始（头之后），按 FileAlignment=0x200 对齐
    fo = 0x400
    for s in merged:
        s["foff"] = fo
        fo += (len(s["data"]) + 0x1FF) & ~0x1FF
    size_of_file = fo

    # ---- 符号值 -> RVA ----
    mp = secmap
    name2sec = {s["name"]: s for s in merged}

    def sym_rva(symidx):
        if symidx >= len(syms):
            return None
        sy = syms[symidx]
        if sy["sec"] <= 0:
            return None      # 未定义（应为 0 个）
        if sy["sec"] not in mp:
            return None
        key, base = mp[sy["sec"]]
        return name2sec[key]["rva"] + base + sy["value"]

    # ---- 应用重定位 ----
    nrel = 0
    for s in merged:
        for r in s["rels"]:
            t = r["type"]
            if t == IMAGE_REL_I386_ABSOLUTE:
                continue
            trva = sym_rva(r["sym"])
            if trva is None:
                print("  ★ 无法解析重定位 sym#%d type=%d" % (r["sym"], t))
                continue
            off = r["va"]
            if off + 4 > len(s["data"]):
                print("  ★ 重定位越界: %s+0x%X (节大小 %d)" % (s["name"], off, len(s["data"])))
                continue
            if t == IMAGE_REL_I386_DIR32:
                struct.pack_into("<I", s["data"], off, IMAGE_BASE + trva)
            elif t == IMAGE_REL_I386_REL32:
                # 目标 = 下一条指令地址 + 位移
                site = s["rva"] + off
                rel = (IMAGE_BASE + trva) - (IMAGE_BASE + site + 4)
                struct.pack_into("<i", s["data"], off, rel)
            else:
                print("  ★ 未知重定位类型 %d" % t)
            nrel += 1
    print("  应用重定位 %d 个" % nrel)

    # ---- 导出表 ----
    # 找导出符号（__declspec(dllexport) 的会出现在 .drectve 里 /EXPORT:）
    exports = []
    drectve = next((s for s in secs if s["name"] == ".drectve"), None)
    if drectve:
        txt = bytes(drectve["raw"]).decode("latin1", "replace")
        import re
        for m in re.finditer(r"/EXPORT:([A-Za-z_][A-Za-z0-9_@$?]*)", txt):
            exports.append(m.group(1))
    print("  导出符号: %s" % exports)

    # 为导出表分配空间（放在最后一个节之后）
    n_exp = len(exports)
    exp_rva = 0
    exp_size = 0
    if n_exp:
        # 导出目录 + 名称表
        # IMAGE_EXPORT_DIRECTORY (40 字节) + EAT(4*n) + ENPT(4*n) + EOT(2*n) + names + dllname
        dllname = os.path.basename(out_path).encode() + b"\x00"
        addr_off = 40
        npt_off = addr_off + 4 * n_exp
        ot_off = npt_off + 4 * n_exp
        names_off = ot_off + 2 * n_exp
        # 名称偏移
        name_offs = []
        cur = names_off
        blob = bytearray()
        for e in exports:
            name_offs.append(cur)
            nb = e.encode() + b"\x00"
            blob += nb
            cur += len(nb)
        dllname_off = cur
        blob += dllname
        total = names_off + len(blob)
        total = (total + 0xF) & ~0xF
        exp_data = bytearray(total)
        struct.pack_into("<I", exp_data, 12, 1)              # Base
        struct.pack_into("<I", exp_data, 16, n_exp)          # NumberOfFunctions
        struct.pack_into("<I", exp_data, 20, n_exp)          # NumberOfNames
        struct.pack_into("<I", exp_data, 28, npt_off)        # AddressOfNames
        struct.pack_into("<I", exp_data, 32, ot_off)         # AddressOfNameOrdinals
        exp_data[names_off:names_off + len(blob)] = blob
        for i, e in enumerate(exports):
            struct.pack_into("<I", exp_data, npt_off + 4 * i, name_offs[i])
            struct.pack_into("<H", exp_data, ot_off + 2 * i, i)
        # EAT 稍后填（需要 RVA）
        exp_rva = va
        exp_size = total
        va += (total + 0xFFF) & ~0xFFF
        size_of_image = va
        mk = dict(name=".edata", data=exp_data, flags=IMAGE_SCN_CNT_INITIALIZED_DATA | IMAGE_SCN_MEM_READ,
                  rels=[], rva=exp_rva, foff=fo)
        merged.append(mk)
        fo += (len(exp_data) + 0x1FF) & ~0x1FF
        size_of_file = fo
        # 填 EAT（指向各导出函数的 RVA）
        # 注意：这里只导出符号名，不保证指向真实函数体（骨架阶段）
        for i, e in enumerate(exports):
            struct.pack_into("<I", exp_data, addr_off + 4 * i, exp_rva)

    # ---- 写 PE ----
    num_sec = len(merged)
    opt_size = 224
    hdr_size = 0x400

    dos = bytearray(0x80)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, 0x80)

    # PE 签名 + COFF 头
    pe = bytearray()
    pe += b"PE\x00\x00"
    pe += struct.pack("<HHIIIHH", IMAGE_FILE_MACHINE_I386, num_sec, 0, 0, 0,
                      opt_size, 0x2102)   # DLL | EXECUTABLE_IMAGE | 32BIT

    # Optional Header (PE32)
    oh = bytearray(opt_size)
    struct.pack_into("<H", oh, 0, 0x10B)          # Magic
    oh[2] = 13                                     # MajorLinkerVersion
    struct.pack_into("<I", oh, 4, 0)               # SizeOfCode（稍后）
    struct.pack_into("<I", oh, 8, 0)               # SizeOfInitializedData
    struct.pack_into("<I", oh, 12, 0)              # SizeOfUninitializedData
    struct.pack_into("<I", oh, 16, 0)              # AddressOfEntryPoint（DLL 无入口）
    struct.pack_into("<I", oh, 20, 0x1000)         # BaseOfCode
    struct.pack_into("<I", oh, 24, 0x2000)         # BaseOfData
    struct.pack_into("<I", oh, 28, IMAGE_BASE)     # ImageBase
    struct.pack_into("<I", oh, 32, 0x1000)         # SectionAlignment
    struct.pack_into("<I", oh, 36, 0x200)          # FileAlignment
    struct.pack_into("<H", oh, 40, 4)              # MajorOSVersion
    struct.pack_into("<H", oh, 42, 0)              # MinorOSVersion
    struct.pack_into("<H", oh, 44, 0)
    struct.pack_into("<H", oh, 46, 0)
    struct.pack_into("<H", oh, 48, 4)              # MajorSubsystemVersion
    struct.pack_into("<H", oh, 50, 0)
    struct.pack_into("<I", oh, 52, 0)              # Win32VersionValue
    struct.pack_into("<I", oh, 56, size_of_image)  # SizeOfImage
    struct.pack_into("<I", oh, 60, hdr_size)       # SizeOfHeaders
    struct.pack_into("<I", oh, 64, 0)              # CheckSum
    struct.pack_into("<H", oh, 68, 2)              # Subsystem = GUI
    struct.pack_into("<H", oh, 70, 0x0140)         # DllCharacteristics
    struct.pack_into("<I", oh, 72, 0x100000)       # SizeOfStackReserve
    struct.pack_into("<I", oh, 76, 0x1000)         # SizeOfStackCommit
    struct.pack_into("<I", oh, 80, 0x100000)       # SizeOfHeapReserve
    struct.pack_into("<I", oh, 84, 0x1000)         # SizeOfHeapCommit
    struct.pack_into("<I", oh, 88, 0)              # LoaderFlags
    struct.pack_into("<I", oh, 92, 16)             # NumberOfRvaAndSizes
    # DataDirectory[0] = Export
    if n_exp:
        struct.pack_into("<II", oh, 96, exp_rva, exp_size)

    # 节表
    sh = bytearray()
    for s in merged:
        ent = bytearray(40)
        nm = s["name"].encode()[:8]
        ent[0:len(nm)] = nm
        struct.pack_into("<I", ent, 8, len(s["data"]))          # VirtualSize
        struct.pack_into("<I", ent, 12, s["rva"])               # VirtualAddress
        struct.pack_into("<I", ent, 16, (len(s["data"]) + 0x1FF) & ~0x1FF)  # SizeOfRawData
        struct.pack_into("<I", ent, 20, s["foff"])              # PointerToRawData
        struct.pack_into("<I", ent, 36, s["flags"])             # Characteristics
        sh += ent

    out = bytearray(hdr_size)
    out[0:len(dos)] = dos
    out[0x80:0x80 + len(pe)] = pe
    out[0x80 + len(pe):0x80 + len(pe) + opt_size] = oh
    out[0x80 + len(pe) + opt_size:0x80 + len(pe) + opt_size + len(sh)] = sh

    # 节数据
    for s in merged:
        p = s["foff"]
        if p + len(s["data"]) > len(out):
            out += b"\x00" * (p + len(s["data"]) - len(out))
        out[p:p + len(s["data"])] = s["data"]

    if len(out) < size_of_file:
        out += b"\x00" * (size_of_file - len(out))

    open(out_path, "wb").write(bytes(out))
    print()
    print("✓ 生成 %s (%d 字节, %d 节, 导出 %d 个)" %
          (out_path, len(out), num_sec, n_exp))
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
