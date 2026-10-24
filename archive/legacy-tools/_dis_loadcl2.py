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
start=0x7F44FB; ln=0x1A0
off=va2off(start)
print('loadcharlist body',hex(start))
for ins in md.disasm(data[off:off+ln], start):
    mk=''
    for g in (0x2528B2C,0x2528B30,0x2528B28,0x2528B34,0x2528B38):
        if format(g,'x') in ins.op_str: mk=' <<'+hex(g)
    print(f'  {ins.address:08X}: {ins.mnemonic:7s} {ins.op_str}{mk}')
    if ins.mnemonic=='ret': break
