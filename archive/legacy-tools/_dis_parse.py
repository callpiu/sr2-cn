# -*- coding: utf-8 -*-
import pefile
from capstone import *
EXE=r'G:/SteamLibrary/steamapps/common/Saints Row 2/SR2_pc.exe'
pe=pefile.PE(EXE, fast_load=True); ib=pe.OPTIONAL_HEADER.ImageBase
data=open(EXE,'rb').read()
def va2off(va):
    rva=va-ib
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData):
            return s.PointerToRawData+(rva-s.VirtualAddress)
md=Cs(CS_ARCH_X86, CS_MODE_32)
for start,ln,label in [(0x7F43C0,0x300,'parse_charlist(0x7F43C0)'),(0x7F4AD0,0x180,'font_init_callee?')]:
    off=va2off(start)
    print('\n'+'='*72); print(label,hex(start)); print('='*72)
    for ins in md.disasm(data[off:off+ln], start):
        mk=''
        for g in (0x2528B2C,0x2528B30,0x2528B28,0x2528B34,0x2528B38,0x2528B29):
            if format(g,'x') in ins.op_str: mk=' <<'+hex(g)
        if '+ 2]' in ins.op_str: mk+=' <<+2'
        print(f'  {ins.address:08X}: {ins.mnemonic:7s} {ins.op_str}{mk}')
        if ins.mnemonic=='ret': break
