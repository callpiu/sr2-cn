# -*- coding: utf-8 -*-
"""DFEngine.dll 逆向：节表 + 把运行时 VA 映射回文件偏移并反汇编。"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
import pefile, capstone

P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll"
pe = pefile.PE(P)
IB = pe.OPTIONAL_HEADER.ImageBase
RT_BASE = 0x5C640000
print("ImageBase=0x%X  RuntimeBase=0x%X" % (IB, RT_BASE))
print("Sections:")
for s in pe.sections:
    nm = s.Name.rstrip(b"\x00").decode(errors="replace")
    print("  %-8s VA=0x%08X VSz=0x%X Raw=0x%X RawSz=0x%X" % (
        nm, s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData))


def rt_to_rva(rt):
    return rt - RT_BASE


def va_to_off(va):
    rva = va - IB
    return pe.get_offset_from_rva(rva)


def rt_bytes(rt, n):
    off = va_to_off(rt - RT_BASE + IB)
    return pe.__data__[off: off + n]


def disasm(rt, n, label=""):
    print("\n--- %s  0x%08X ---" % (label, rt))
    off = va_to_off(rt - RT_BASE + IB)
    code = pe.__data__[off: off + n]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    for ins in md.disasm(code, rt):
        print("  %08X: %-22s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))


# hook 桩转发目标：0x5C6ECE20 -> call 0x5C6ECDB0
disasm(0x5C6ECDB0, 200, "0x5C6ECDB0 (stub callee)")
