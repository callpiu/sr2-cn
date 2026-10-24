# -*- coding: utf-8 -*-
"""用 PDB 解析出的符号 RVA 反汇编 DFEngine 关键函数。
RVA = segment_offset + 0x1000 (由 _CreateDFEngine 0x706D0 -> export 0x716D0 验证)
"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
import capstone

P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll"
data = open(P, "rb").read()
import pefile
pe = pefile.PE(P)
RT_BASE = 0x5C640000
IB = pe.OPTIONAL_HEADER.ImageBase


def va(off):
    return RT_BASE + off + 0x1000


def bytes_at_rva(rva, n):
    o = pe.get_offset_from_rva(rva)
    return data[o:o + n]


def dis(rva, n, label):
    v = RT_BASE + rva
    code = bytes_at_rva(rva, n)
    print("\n" + "=" * 70)
    print("--- %s  RVA=0x%X  VA=0x%08X ---" % (label, rva, v))
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    for ins in md.disasm(code, v):
        line = "  %08X: %-24s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str)
        print(line)
        if ins.mnemonic in ("ret", "jmp") and ins.address > v + 30:
            break


dis(0xAA440 + 0x1000, 420, "MStrings::StartParsing")
