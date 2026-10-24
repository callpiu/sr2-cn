# -*- coding: utf-8 -*-
"""反汇编引用 charlist 全局(0x02528B2C/0x02528B30)的代码区。"""
import struct, sys
sys.stdout.reconfigure(encoding="utf-8")
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile

PATH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
pe = pefile.PE(PATH)
base = pe.OPTIONAL_HEADER.ImageBase
print("ImageBase = 0x%X" % base)
data = open(PATH, "rb").read()

def va2off(va):
    for s in pe.sections:
        if s.VirtualAddress <= va - base < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (va - base - s.VirtualAddress)
    return None

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = False

REGIONS = [(0x3f4d80, 0x3f5260, "charlist 引用密集区"),
           (0x3ed800, 0x3ed960, "另一处引用")]

for lo, hi, tag in REGIONS:
    o0, o1 = va2off(base + lo), va2off(base + hi)
    print("\n" + "=" * 90)
    print("=== %s  VA 0x%08X - 0x%08X ===" % (tag, base + lo, base + hi))
    print("=" * 90)
    code = data[o0:o1]
    for ins in md.disasm(code, base + lo):
        mark = ""
        if "0x2528b2c" in ins.op_str or "0x2528b30" in ins.op_str or "0x2528b28" in ins.op_str:
            mark = "   <<<< CHARLIST"
        print("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ins.op_str, mark))
