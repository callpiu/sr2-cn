# -*- coding: utf-8 -*-
"""反汇编 validate(0x7F4E30) 的 4 个调用者的上下文；
以及 glyph->char(0x7F4EE0) 的调用者 0x7ED855。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
import pefile

PATH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe"
pe = pefile.PE(PATH)
base = pe.OPTIONAL_HEADER.ImageBase
buf = open(PATH, "rb").read()
text = [s for s in pe.sections if s.Name.startswith(b".text")][0]
tstart = base + text.VirtualAddress
def va2off(va):
    return text.PointerToRawData + (va - base - text.VirtualAddress)
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = False
# context: 0x60 bytes before each caller
CALLEES = [("validate", 0x80DB5B), ("validate", 0x839BF3), ("validate", 0x863243),
           ("validate", 0x9D42D6), ("glyph->char", 0x7ED855)]
for name, ca in CALLEES:
    lo = ca - 0x70; hi = ca + 0x30
    o0, o1 = va2off(lo), va2off(hi)
    print("\n" + "=" * 96)
    print("=== 调用点 0x%08X  （%s） ===" % (ca, name))
    print("=" * 96)
    for ins in md.disasm(buf[o0:o1], lo):
        m = ""
        if ins.address == ca: m = "   <<<< CALL"
        if "0x2528b" in ins.op_str: m += "  [CHARLIST GLOBAL]"
        print("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ins.op_str, m))
