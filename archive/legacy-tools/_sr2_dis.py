# -*- coding: utf-8 -*-
"""反汇编 sr2_pc.exe 的关键文本函数：StringsLoad(0x7F4780) / 0x7F46E4 站点 / loadcharlist(0x7F4430)。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import capstone, pefile

P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
data = open(P, "rb").read()
pe = pefile.PE(P)
IB = pe.OPTIONAL_HEADER.ImageBase


def bytes_va(va, n):
    o = pe.get_offset_from_rva(va - IB)
    return data[o:o + n]


def dis(va, n, label):
    print("\n" + "=" * 74)
    print("--- %s VA=0x%08X ---" % (label, va))
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    for ins in md.disasm(bytes_va(va, n), va):
        print("  %08X: %-22s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))


for va, n, lb in [
    (0x7F46E4, 40, "AddStrings hook site (0x7F46E4)"),
    (0x7F4780, 260, "StringsLoad (0x7F4780)"),
    (0x7F4430, 120, "loadcharlist (0x7F4430)"),
    (0x7F4CF0, 40, "get_language_code (0x7F4CF0)"),
    (0x7F4F60, 120, "compress_character (0x7F4F60)"),
]:
    dis(va, n, lb)
