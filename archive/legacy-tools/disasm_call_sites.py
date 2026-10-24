# -*- coding: utf-8 -*-
"""反汇编 11 个 0x7F5030 调用点各自所在的函数上下文（前后各 80 字节）。
目的：找出「HUD/活动字幕」路径是哪一处 —— 特征是不调用 validate(0x7F4E30) 或直接从 slot 表来。"""
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

sites = [0x75D5A0, 0x80DB76, 0x81590C, 0x8160AC, 0x816EFC,
         0x819B5A, 0x819E6C, 0x819F25, 0x839C05, 0x863255, 0x9D42E5]
for c in sites:
    lo, hi = c - 0x60, c + 0x20
    o0, o1 = va2off(lo), va2off(hi)
    print("\n" + "=" * 90)
    print("=== 调用点 0x%08X 上下文 ===" % c)
    for ins in md.disasm(buf[o0:o1], lo):
        mark = "  <<<< CALL 0x7F5030" if ins.address == c else ""
        print("  0x%08X  %-9s %s%s" % (ins.address, ins.mnemonic, ins.op_str, mark))
