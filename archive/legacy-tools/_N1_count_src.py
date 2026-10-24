# -*- coding: utf-8 -*-
"""追踪 0x7F4430 里 [esp+0x10] 的来源（循环上限=字符总数）"""
import capstone
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
BASE=0x400000
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
start=0x3F4570; end=0x3F45F8
for ins in md.disasm(raw[start:end], BASE+start):
    m=""
    if 'esp + 0x10' in ins.op_str or '0xe26080' in ins.op_str or '0xc97089' in ins.op_str or '0x2a15730' in ins.op_str:
        m="   <== 关键"
    print("0x%08X  %-8s %s%s" % (ins.address, ins.mnemonic, ins.op_str, m))
