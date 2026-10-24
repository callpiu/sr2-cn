# -*- coding: utf-8 -*-
"""完整反汇编 0x7ED800-0x7ED960 与 0x7F4400-0x7F5100 全簇。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile

PATH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
pe = pefile.PE(PATH)
base = pe.OPTIONAL_HEADER.ImageBase
buf = open(PATH, "rb").read()
def va2off(va):
    for s in pe.sections:
        if base + s.VirtualAddress <= va < base + s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (va - base - s.VirtualAddress)
    return None

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = False
REGIONS = [(0x7F4440, 0x7F46B0, "A: 0x7F4461/0x7F466A 引用"),
           (0x7F4F60, 0x7F5100, "B: 0x7F4F79/0x7F4FC6/0x7F504D 引用"),
           (0x7ED860, 0x7ED8C0, "C: 0x7ED88F/0x7ED89B 引用")]
for lo, hi, tag in REGIONS:
    o0, o1 = va2off(lo), va2off(hi)
    print("\n" + "=" * 100)
    print("=== %s  VA 0x%08X - 0x%08X ===" % (tag, lo, hi))
    print("=" * 100)
    for ins in md.disasm(buf[o0:o1], lo):
        m = "   <<<< CHARLIST" if ("0x2528b2" in ins.op_str or "0x2528b3" in ins.op_str) else ""
        print("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ins.op_str, m))
