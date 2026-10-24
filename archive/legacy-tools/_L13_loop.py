# -*- coding: utf-8 -*-
import capstone
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
BASE=0x400000
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
start=0x3F4590; end=0x3F4676
for ins in md.disasm(raw[start:end], BASE+start):
    line="0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str)
    mark=""
    if 'esp + 0x14' in ins.op_str or 'esp + 0x20' in ins.op_str or 'esp + 0x10' in ins.op_str:
        mark="   <== 关键"
    print(line+mark)
