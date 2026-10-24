# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
import capstone, pefile
P = r"G:/SteamLibrary/steamapps/common/Saints Row 2/SR2_pc.exe"
data = open(P,"rb").read(); pe=pefile.PE(P); IB=pe.OPTIONAL_HEADER.ImageBase
def bs(va,n): 
    o=pe.get_offset_from_rva(va-IB); return data[o:o+n]
def dis(va,n,lb):
    print("\n"+"="*74); print("--- %s VA=0x%08X ---"%(lb,va))
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
    for ins in md.disasm(bs(va,n),va):
        print("  %08X: %-20s %s %s"%(ins.address,ins.bytes.hex(),ins.mnemonic,ins.op_str))
dis(0x7F5030, 130, "codepoint->glyph (render main)")
dis(0x9D42D6, 40, "HUD pipeline call site")
dis(0x9D42E5, 40, "HUD pipeline call site2")
