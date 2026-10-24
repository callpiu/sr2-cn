# -*- coding: utf-8 -*-
"""反汇编 DFEngine 文本渲染路径：vint_sr2_render(0x96340) / vint_element_base_render(0x96DB0) / Init(0x97B40)。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import capstone, pefile

P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll"
data = open(P, "rb").read()
pe = pefile.PE(P)
RT = 0x5C640000


def bytes_rva(rva, n):
    o = pe.get_offset_from_rva(rva)
    return data[o:o + n]


def dis(rva, n, label):
    print("\n" + "=" * 74)
    print("--- %s RVA=0x%X VA=0x%08X ---" % (label, rva, RT + rva))
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    for ins in md.disasm(bytes_rva(rva, n), RT + rva):
        print("  %08X: %-24s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))


dis(0x96340, 200, "Render2D::vint_sr2_render")
dis(0x96DB0, 200, "Render2D::vint_element_base_render")
dis(0x97B40, 160, "Render2D::Init")
