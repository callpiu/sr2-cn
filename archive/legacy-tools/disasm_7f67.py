# -*- coding: utf-8 -*-
"""反汇编 0x7F6700-0x7F6E00 —— 另一簇引用 0x2528B40/0x2528B44 的代码。
这是独立于 0x7F4xxx 的第二套字表逻辑，极可能是 HUD/活动字幕路径。"""
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
lo, hi = 0x7F6700, 0x7F6E20
o0, o1 = va2off(lo), va2off(hi)
out = []
for ins in md.disasm(buf[o0:o1], lo):
    m = ""
    if "0x2528b4" in ins.op_str or "0x2528b3" in ins.op_str or "0x2528b2" in ins.op_str:
        m = "   <<<< GLOBAL"
    out.append("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ins.op_str, m))
print("\n".join(out))
print("\n共 %d 条指令" % len(out))
for line in out:
    if "GLOBAL" in line:
        print(line)
