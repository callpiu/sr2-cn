# -*- coding: utf-8 -*-
"""反汇编引用 cxt 字符串的代码：StartParsingUSFallback(0xAC340) / 0xACA39 附近。"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
import capstone, pefile

P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll"
data = open(P, "rb").read()
pe = pefile.PE(P)
RT = 0x5C640000


def bytes_rva(rva, n):
    o = pe.get_offset_from_rva(rva)
    return data[o:o + n]


def dis(rva, n, label):
    v = RT + rva
    print("\n" + "=" * 72)
    print("--- %s RVA=0x%X VA=0x%08X ---" % (label, rva, v))
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    for ins in md.disasm(bytes_rva(rva, n), v):
        print("  %08X: %-22s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))


dis(0xAC340, 300, "StartParsingUSFallback")
