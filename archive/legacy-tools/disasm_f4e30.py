# -*- coding: utf-8 -*-
"""完整反汇编 0x7F4E30 校验函数 与 0x7F4EE0 附近函数。
ImageBase = 0x400000 无 ASLR，静态 VA = 绝对地址。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile

PATH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
pe = pefile.PE(PATH)
base = pe.OPTIONAL_HEADER.ImageBase
data = open(PATH, "rb").read()
print("ImageBase = 0x%X  size=0x%X" % (base, len(data)))

def va2off(va):
    for s in pe.sections:
        if s.VirtualAddress + base <= va < s.VirtualAddress + base + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return s.PointerToRawData + (va - s.VirtualAddress - base)
    return None

md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = False

REGIONS = [(0x7F4E00, 0x7F5130, "校验区/0x7F4E30")]

for lo, hi, tag in REGIONS:
    o0, o1 = va2off(lo), va2off(hi)
    print("\n" + "=" * 100)
    print("=== %s  VA 0x%08X - 0x%08X ===" % (tag, lo, hi))
    print("=" * 100)
    code = data[o0:o1]
    for ins in md.disasm(code, lo):
        mark = ""
        ops = ins.op_str
        if "0x2528b2c" in ops or "0x2528b30" in ops or "0x2528b28" in ops:
            mark = "   <<<< CHARLIST GLOBAL"
        print("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ops, mark))
