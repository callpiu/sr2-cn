# -*- coding: utf-8 -*-
"""反汇编 0x9D4200-0x9D4400 —— 同时调用 validate(0x7F4E30) 与 convert(0x7F5030) 的函数。
这是 4 个 validate 调用者中最独立的一处，很可能就是活动/HUD 字幕路径。"""
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
lo, hi = 0x9D4200, 0x9D4400
o0, o1 = va2off(lo), va2off(hi)
for ins in md.disasm(buf[o0:o1], lo):
    mark = ""
    if ins.address in (0x9D42D6, 0x9D42E5):
        mark = "   <<<< KEY CALL"
    if "0x2528b" in ins.op_str:
        mark += "  <<<< CHARLIST GLOBAL"
    print("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ins.op_str, mark))
