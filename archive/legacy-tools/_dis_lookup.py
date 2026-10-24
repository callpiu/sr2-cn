# -*- coding: utf-8 -*-
"""反汇编 0x7F4E30 / 0x7F4EE0 字表查找函数"""
import pefile
from capstone import *

EXE=r'G:/SteamLibrary/steamapps/common/Saints Row 2/SR2_pc.exe'
pe=pefile.PE(EXE, fast_load=True)
ib=pe.OPTIONAL_HEADER.ImageBase
print('ImageBase',hex(ib))

data=open(EXE,'rb').read()
def va2off(va):
    rva=va-ib
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData):
            return s.PointerToRawData+(rva-s.VirtualAddress)
    return None

md=Cs(CS_ARCH_X86, CS_MODE_32)
md.detail=True

for start,ln,label in [(0x7F4E30,0x140,'校验函数?' ),(0x7F4EE0,0x180,'可疑函数(+2半字)')]:
    off=va2off(start)
    print('\n'+'='*70)
    print(f'{label}  VA={hex(start)}  off={hex(off) if off else None}')
    print('='*70)
    code=data[off:off+ln]
    for ins in md.disasm(code, start):
        mark=''
        # 标记对字表全局的访问
        for g in (0x2528B2C,0x2528B30,0x2528B28,0x2528B34,0x2528B38):
            if hex(g) in ins.op_str.replace('0x','0x'):
                mark=' <<GLOBAL '+hex(g)
        if '[edi + 2]' in ins.op_str or '[edi+2]' in ins.op_str or '+ 2]' in ins.op_str:
            mark+=' <<PLUS2'
        print(f'  {ins.address:08X}: {ins.mnemonic:8s} {ins.op_str}{mark}')
