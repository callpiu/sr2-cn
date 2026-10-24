# -*- coding: utf-8 -*-
"""反汇编 0x7ED800-0x7ED960：另一处同时引用 charlist 全局的代码。
这是除 0x7F4xxx 簇之外唯一的另一个引用点，很可能是 HUD 路径。"""
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
lo, hi = 0x7ED7E0, 0x7ED960
o0, o1 = va2off(lo), va2off(hi)
for ins in md.disasm(buf[o0:o1], lo):
    m = ""
    if "0x2528b" in ins.op_str:
        m = "   <<<< CHARLIST GLOBAL"
    print("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ins.op_str, m))
