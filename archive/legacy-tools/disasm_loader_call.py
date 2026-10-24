# -*- coding: utf-8 -*-
"""反汇编 0x7F4700-0x7F4790 —— 加载器 0x7F4430 的调用点，弄清调用约定与参数。"""
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
lo, hi = 0x7F4700, 0x7F47A0
o0, o1 = va2off(lo), va2off(hi)
for ins in md.disasm(buf[o0:o1], lo):
    mark = "   <<<< CALL LOADER" if ins.address == 0x7F4762 else ""
    print("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ins.op_str, mark))
