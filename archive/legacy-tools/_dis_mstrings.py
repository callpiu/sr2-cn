# -*- coding: utf-8 -*-
import pefile
from capstone import *
DLL=r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll"
pe=pefile.PE(DLL, fast_load=True)
data=open(DLL,'rb').read()
def rva2off(rva):
    for s in pe.sections:
        if s.VirtualAddress<=rva<s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData):
            return s.PointerToRawData+(rva-s.VirtualAddress)
md=Cs(CS_ARCH_X86, CS_MODE_32)
for rva,ln,label in [(0xACCC0,0x400,'MStrings::loadcharlist'),(0xAB370,0x300,'MStrings::get_localization_from_hash')]:
    off=rva2off(rva)
    print('\n'+'='*74); print(label,hex(rva)); print('='*74)
    for ins in md.disasm(data[off:off+ln], rva):
        print(f'  {ins.address:06X}: {ins.mnemonic:8s} {ins.op_str}')
        if ins.mnemonic=='ret': break
