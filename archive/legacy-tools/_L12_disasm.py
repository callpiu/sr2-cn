# -*- coding: utf-8 -*-
"""反汇编 0x3F4400..0x3F4E00 (loadcharlist 及相关)"""
import capstone
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
BASE=0x400000
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
start=0x3F4400; end=0x3F4E20
code=raw[start:end]
for ins in md.disasm(code, BASE+start):
    print("0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
