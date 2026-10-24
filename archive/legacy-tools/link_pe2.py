# -*- coding: utf-8 -*-
"""COFF (.obj) -> PE32 DLL 最小链接器（v2，干净重写）。

支持
    · 合并同名节（.text/.rdata/.data/.bss/.CRT$XCU 等）
    · .bss（vsize>0, rawsize=0）按虚拟大小零填充
    · x86 重定位：DIR32(6) / REL32(20)
    · 导出表（从 .drectve 的 /EXPORT: 提取）
    · 零导入（代码用 PEB 自解析 kernel32）

用法
    python link_pe2.py in.obj out.dll
"""
import os
import re
import sys
import struct

MACHINE_I386 = 0x014C
REL_ABSOLUTE = 0x0000
REL_DIR32 = 0x0006
REL_REL32 = 0x0014

SCN_CODE = 0x00000020
SCN_IDATA = 0x00000040
SCN_UDATA = 0x00000080
SCN_MEM_EXEC = 0x20000000
SCN_MEM_READ = 0x40000000
SCN_MEM_WRITE = 0x80000000


def parse_coff(data):
    machine, nsec, tds, symoff, nsym, optsz, chars = struct.unpack_from("<HHIIIHH", data, 0)
    if machine != MACHINE_I386:
        raise SystemExit("不是 x86 COFF (machine=0x%04X)" % machine)
    strtab_off = symoff + nsym * 18
    strtab_size, = struct.unpack_from("<I", data, strtab_off)

    def read_str(off):
        p = strtab_off + off
        e = data.index(b"\x00", p)
        return data[p:e].decode("latin1")

    def secname(nm8):
        if nm8[:1] == b"/" and nm8[1:2].isdigit():
            return read_str(int(nm8[1:].split(b"\x00")[0]))
        return nm8.rstrip(b"\x00").decode("latin1")

    def symname(nm8):
        if nm8[:4] == b"\x00\x00\x00\x00":
            return read_str(struct.unpack_from("<I", nm8, 4)[0])
        return nm8.rstrip(b"\x00").decode("latin1")

    # 建立【按原始索引】的符号表（辅助记录槽位填父符号）
    syms = [None] * nsym
    i = 0
    while i < nsym:
        o = symoff + i * 18
        nm8 = data[o:o + 8]
        val, secnum, typ, cls, naux = struct.unpack_from("<IhHBB", data, o + 8)
        entry = dict(idx=i, name=symname(nm8), value=val, sec=secnum,
                     type=typ, cls=cls, naux=naux)
        syms[i] = entry
        for k in range(1, naux + 1):
            if i + k < nsym:
                syms[i + k] = entry
        i += 1 + naux

    secs = []
    for i in range(nsec):
        o = 20 + optsz + i * 40
        nm8 = data[o:o + 8]
        vs, va, rs, rp, relp, lnp, nrel, nln, fl = struct.unpack_from("<IIIIIIHHI", data, o + 8)
        rels = []
        for k in range(nrel):
            ro = relp + k * 10
            rva, si, ty = struct.unpack_from("<IIH", data, ro)
            rels.append((rva, si, ty))
        if rs and rp:
            raw = bytearray(data[rp:rp + rs])
        else:
            raw = bytearray(vs)          # .bss 等
        secs.append(dict(idx=i + 1, name=secname(nm8), vsize=vs, raw=raw,
                         flags=fl, rels=rels))
    return secs, syms


def build(obj_path, out_path):
    data = open(obj_path, "rb").read()
    secs, syms = parse_coff(data)

    # ---- 修正 .bss / 未初始化节的尺寸（COFF 里 vsize/rawsize 可能为 0）----
    maxval = {}
    for sy in syms:
        if sy is None:
            continue
        if sy["sec"] > 0:
            maxval[sy["sec"]] = max(maxval.get(sy["sec"], 0), sy["value"] + 8)
    for s in secs:
        need = maxval.get(s["idx"], 0)
        if len(s["raw"]) < need:
            s["raw"] += b"\x00" * (need - len(s["raw"]))
            s["vsize"] = need

    # ---- 合并同名节，建立 secmap ----
    merged = {}
    order = []
    secmap = {}
    for s in secs:
        k = s["name"]
        if k not in merged:
            merged[k] = dict(name=k, data=bytearray(), flags=0, rels=[])
            order.append(k)
        m = merged[k]
        align = 16 if (s["flags"] & SCN_CODE) else 8
        m["data"] += b"\x00" * ((-len(m["data"])) % align)
        off = len(m["data"])
        m["data"] += s["raw"]
        m["flags"] |= s["flags"]
        for (rva, si, ty) in s["rels"]:
            m["rels"].append((off + rva, si, ty))
        secmap[s["idx"]] = (k, off)

    mlist = [merged[k] for k in order]
    print("合并后 %d 节:" % len(mlist))
    for m in mlist:
        print("  %-14s %6d 字节 relocs=%-3d flags=0x%08X" %
              (m["name"], len(m["data"]), len(m["rels"]), m["flags"]))
    print("  secmap: %s" % {k: v for k, v in sorted(secmap.items())})

    # ---- 布局 ----
    BASE = 0x10000000
    va = 0x1000
    for m in mlist:
        m["rva"] = va
        m["vsize"] = len(m["data"])
        va += (m["vsize"] + 0xFFF) & ~0xFFF
    # 导出表放最后
    n_exp = 0
    exp_rva = exp_size = 0

    drectve = merged.get(".drectve")
    exports = []
    if drectve:
        txt = bytes(drectve["data"]).decode("latin1", "replace")
        exports = re.findall(r"/EXPORT:([A-Za-z_][\w@$?]*)", txt)
    n_exp = len(exports)
    print("  导出: %s" % exports)

    if n_exp:
        dllname = os.path.basename(out_path).encode() + b"\x00"
        addr_off = 40
        npt_off = addr_off + 4 * n_exp
        ot_off = npt_off + 4 * n_exp
        names_off = ot_off + 2 * n_exp
        name_offs = []
        blob = bytearray()
        cur = names_off
        for e in exports:
            name_offs.append(cur)
            nb = e.encode() + b"\x00"
            blob += nb
            cur += len(nb)
        dllname_off = cur
        blob += dllname
        total = (names_off + len(blob) + 0xF) & ~0xF
        exp_data = bytearray(total)
        # IMAGE_EXPORT_DIRECTORY 字段偏移：
        #   +12 Name  +16 Base  +20 NumberOfFunctions  +24 NumberOfNames
        #   +28 AddressOfFunctions  +32 AddressOfNames  +36 AddressOfNameOrdinals
        # Name 在下面回填
        struct.pack_into("<I", exp_data, 16, 1)                # Base
        struct.pack_into("<I", exp_data, 20, n_exp)            # NumberOfFunctions
        struct.pack_into("<I", exp_data, 24, n_exp)            # NumberOfNames
        exp_data[names_off:names_off + len(blob)] = blob
        for i, e in enumerate(exports):
            struct.pack_into("<H", exp_data, ot_off + 2 * i, i)
            struct.pack_into("<I", exp_data, addr_off + 4 * i, 0)   # 稍后填
        exp_rva = va
        exp_size = total
        # ★ 所有地址字段都必须是 RVA（= 节 RVA + 节内偏移）
        struct.pack_into("<I", exp_data, 12, exp_rva + dllname_off)   # Name
        struct.pack_into("<I", exp_data, 28, exp_rva + addr_off)      # AddressOfFunctions
        struct.pack_into("<I", exp_data, 32, exp_rva + npt_off)       # AddressOfNames
        struct.pack_into("<I", exp_data, 36, exp_rva + ot_off)        # AddressOfNameOrdinals
        for i in range(n_exp):
            struct.pack_into("<I", exp_data, npt_off + 4 * i, exp_rva + name_offs[i])
        va += (total + 0xFFF) & ~0xFFF
        mlist.append(dict(name=".edata", data=exp_data, flags=SCN_IDATA | SCN_MEM_READ,
                          rels=[], rva=exp_rva, vsize=total))
        merged[".edata"] = mlist[-1]

    size_of_image = va



    # 文件偏移
    fo = 0x400
    for m in mlist:
        m["foff"] = fo
        fo += (len(m["data"]) + 0x1FF) & ~0x1FF
    size_of_file = fo

    # ---- 符号 -> RVA ----
    name2sec = {m["name"]: m for m in mlist}

    def sym_rva(si):
        if si >= len(syms):
            return None
        sy = syms[si]
        if sy is None:
            return None
        if sy["sec"] <= 0 or sy["sec"] not in secmap:
            return None
        k, base = secmap[sy["sec"]]
        if k not in name2sec:
            return None
        return name2sec[k]["rva"] + base + sy["value"]

    # ---- 重定位 ----
    # 同时收集需要写入 .reloc 的 HIGHLOW 项（DIR32 绝对地址）
    reloc_entries = []          # (rva, type)
    nok = nbad = 0
    for m in mlist:
        for (off, si, ty) in m["rels"]:
            if ty == REL_ABSOLUTE:
                continue
            trva = sym_rva(si)
            if trva is None:
                print("  ★ 未解析 sym#%d (%s)" % (si, syms[si]["name"] if 0 <= si < len(syms) else "OOB"))
                nbad += 1
                continue
            if off + 4 > len(m["data"]):
                print("  ★ 越界 %s+0x%X (len %d)" % (m["name"], off, len(m["data"])))
                nbad += 1
                continue
            if ty == REL_DIR32:
                struct.pack_into("<I", m["data"], off, BASE + trva)
                # 记录 HIGHLOW 重定位（IMAGE_REL_BASED_HIGHLOW = 3）
                if m["name"] != ".reloc":
                    reloc_entries.append((m["rva"] + off, 3))
            elif ty == REL_REL32:
                site = m["rva"] + off
                struct.pack_into("<i", m["data"], off, (BASE + trva) - (BASE + site + 4))
            else:
                print("  ★ 未知类型 %d" % ty)
                nbad += 1
                continue
            nok += 1
    print("  重定位: 成功 %d, 失败 %d" % (nok, nbad))

    # ---- 生成 .reloc 节 ----
    reloc_rva = reloc_size = 0
    if reloc_entries:
        reloc_entries.sort()
        blocks = bytearray()
        i2 = 0
        while i2 < len(reloc_entries):
            page = reloc_entries[i2][0] & ~0xFFF
            entries = bytearray()
            while i2 < len(reloc_entries) and (reloc_entries[i2][0] & ~0xFFF) == page:
                rva2, ty2 = reloc_entries[i2]
                entries += struct.pack("<HH", (ty2 << 12) | (rva2 & 0xFFF), 0)
                i2 += 1
            blk = struct.pack("<II", page, 8 + len(entries)) + bytes(entries)
            while len(blk) % 4:
                blk += b"\x00\x00"
            blocks += blk
        reloc_rva = va
        reloc_size = len(blocks)
        va += (reloc_size + 0xFFF) & ~0xFFF
        mlist.append(dict(name=".reloc", data=bytearray(blocks),
                          flags=SCN_IDATA | SCN_MEM_READ | 0x02000000,
                          rels=[], rva=reloc_rva, vsize=reloc_size))
        merged[".reloc"] = mlist[-1]
        print("  .reloc: %d 个项, %d 字节, RVA 0x%X" %
              (len(reloc_entries), reloc_size, reloc_rva))
    else:
        print("  .reloc: 无（不需要）")

    # ---- 全部节就绪，重算 SizeOfImage 和文件偏移 ----
    va2 = 0x1000
    for m in mlist:
        if "rva" not in m:
            m["rva"] = va2
        m["vsize"] = len(m["data"])
        va2 = m["rva"] + ((m["vsize"] + 0xFFF) & ~0xFFF)
    size_of_image = va2

    fo = 0x400
    for m in mlist:
        m["foff"] = fo
        fo += (len(m["data"]) + 0x1FF) & ~0x1FF
    size_of_file = fo

    # 若 .reloc 是在导出表之后追加的，更新重定位目录
    if reloc_rva:
        pass    # 已在 oh 里写入（下面）


    # 填导出地址表（AddressOfFunctions，位于 edata 偏移 addr_off）
    if n_exp:
        ed = merged[".edata"]["data"]
        for i, e in enumerate(exports):
            rva = 0
            # 匹配符号：_Name@N / _Name / Name
            for sy in syms:
                if sy is None or sy["sec"] <= 0 or sy["type"] != 0x20:
                    continue
                n = sy["name"]
                base_n = n
                if base_n.startswith("_"):
                    base_n = base_n[1:]
                if "@" in base_n:
                    base_n = base_n.split("@")[0]
                if base_n == e:
                    r = sym_rva(sy["idx"])
                    if r:
                        rva = r
                        break
            print("  导出 %-22s -> RVA 0x%X" % (e, rva))
            struct.pack_into("<I", ed, 40 + 4 * i, rva)



    # ---- 入口点 ----
    entry_rva = 0
    entry_name = ""
    # 优先找 DllMain 类符号
    for sy in syms:
        if sy is None:
            continue
        n = sy["name"]
        if n in ("_DllMainCRTStartup", "_DllMainCRTStartup@12", "DllMain",
                 "_DllMain@12", "DllMainCRTStartup"):
            r = sym_rva(sy["idx"])
            if r:
                entry_rva, entry_name = r, n
                break
    # 退路：找名字含 Init 的导出，或第一个函数
    if not entry_rva:
        cands = []
        for sy in syms:
            if sy is None or sy["sec"] <= 0 or sy["type"] != 0x20:
                continue
            r = sym_rva(sy["idx"])
            if r:
                cands.append((r, sy["name"]))
        cands.sort()
        for r, n in cands:
            if "Init" in n or "DllMain" in n:
                entry_rva, entry_name = r, n
                break
        if not entry_rva and cands:
            entry_rva, entry_name = cands[0]
    print("  入口点 RVA = 0x%X  (%s)" % (entry_rva, entry_name))

    # ---- 输出 PE ----
    num_sec = len(mlist)
    opt_size = 224
    hdr_size = 0x400
    # ---- DOS 头 + 标准 DOS stub ----
    dos = bytearray(0x80)
    dos[0:0x40] = bytes([
        0x4D, 0x5A, 0x90, 0x00, 0x03, 0x00, 0x00, 0x00,
        0x04, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x00, 0x00,
        0xB8, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00,
    ])
    dos[0x40:0x80] = bytes([
        0x0E, 0x1F, 0xBA, 0x0E, 0x00, 0xB4, 0x09, 0xCD,
        0x21, 0xB8, 0x01, 0x4C, 0xCD, 0x21, 0x54, 0x68,
        0x69, 0x73, 0x20, 0x70, 0x72, 0x6F, 0x67, 0x72,
        0x61, 0x6D, 0x20, 0x63, 0x61, 0x6E, 0x6E, 0x6F,
        0x74, 0x20, 0x62, 0x65, 0x20, 0x72, 0x75, 0x6E,
        0x20, 0x69, 0x6E, 0x20, 0x44, 0x4F, 0x53, 0x20,
        0x6D, 0x6F, 0x64, 0x65, 0x2E, 0x0D, 0x0D, 0x0A,
        0x24, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    ])

    pe = bytearray(b"PE\x00\x00")
    pe += struct.pack("<HHIIIHH", MACHINE_I386, num_sec, 0, 0, 0, opt_size, 0x2102 | 0x0100)

    oh = bytearray(opt_size)
    struct.pack_into("<H", oh, 0, 0x10B)
    oh[2] = 14
    struct.pack_into("<I", oh, 4, sum(len(m["data"]) for m in mlist if m["flags"] & SCN_CODE))
    struct.pack_into("<I", oh, 8, sum(len(m["data"]) for m in mlist if m["flags"] & SCN_IDATA))
    struct.pack_into("<I", oh, 12, sum(len(m["data"]) for m in mlist if m["flags"] & SCN_UDATA))
    struct.pack_into("<I", oh, 16, entry_rva)
    struct.pack_into("<I", oh, 20, 0x1000)
    struct.pack_into("<I", oh, 24, 0x2000)
    struct.pack_into("<I", oh, 28, BASE)
    struct.pack_into("<I", oh, 32, 0x1000)
    struct.pack_into("<I", oh, 36, 0x200)
    struct.pack_into("<HH", oh, 40, 4, 0)
    struct.pack_into("<HH", oh, 44, 0, 0)
    struct.pack_into("<HH", oh, 48, 4, 0)
    struct.pack_into("<I", oh, 56, size_of_image)
    struct.pack_into("<I", oh, 60, hdr_size)
    struct.pack_into("<H", oh, 68, 2)
    struct.pack_into("<H", oh, 70, 0x0140)
    struct.pack_into("<I", oh, 72, 0x100000)
    struct.pack_into("<I", oh, 76, 0x1000)
    struct.pack_into("<I", oh, 80, 0x100000)
    struct.pack_into("<I", oh, 84, 0x1000)
    struct.pack_into("<I", oh, 92, 16)
    if n_exp:
        struct.pack_into("<II", oh, 96, exp_rva, exp_size)
    if reloc_rva:
        struct.pack_into("<II", oh, 136, reloc_rva, reloc_size)   # DataDirectory[5]

    sh = bytearray()
    for m in mlist:
        ent = bytearray(40)
        nb = m["name"].encode()[:8]
        ent[0:len(nb)] = nb
        struct.pack_into("<I", ent, 8, m["vsize"])
        struct.pack_into("<I", ent, 12, m["rva"])
        struct.pack_into("<I", ent, 16, (len(m["data"]) + 0x1FF) & ~0x1FF)
        struct.pack_into("<I", ent, 20, m["foff"])
        struct.pack_into("<I", ent, 36, m["flags"])
        sh += ent

    out = bytearray(hdr_size)
    out[0:len(dos)] = dos
    out[0x80:0x80 + len(pe)] = pe
    out[0x80 + len(pe):0x80 + len(pe) + opt_size] = oh
    out[0x80 + len(pe) + opt_size:0x80 + len(pe) + opt_size + len(sh)] = sh

    for m in mlist:
        p = m["foff"]
        if p + len(m["data"]) > len(out):
            out += b"\x00" * (p + len(m["data"]) - len(out))
        out[p:p + len(m["data"])] = m["data"]
    if len(out) < size_of_file:
        out += b"\x00" * (size_of_file - len(out))

    open(out_path, "wb").write(bytes(out))
    print()
    print("✓ %s: %d 字节, %d 节, 导出 %d, SizeOfImage=0x%X" %
          (out_path, len(out), num_sec, n_exp, size_of_image))
    return out_path


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
