# -*- coding: utf-8 -*-
import pefile
from capstone import *
def mk(path):
    pe=pefile.PE(path, fast_load=True); data=open(path,'rb').read()
    def r2o(rva):
        for s in pe.sections:
            if s.VirtualAddress<=rva<s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData):
                return s.PointerToRawData+(rva-s.VirtualAddress)
    return pe,data,r2o
md=Cs(CS_ARCH_X86, CS_MODE_32)

# SR2_pc.exe!0x7F4D60 (VA, ImageBase 0x400000 -> rva 0x3F4D60)
pe,data,r2o=mk(r"G:\SteamLibrary\steamapps\common\Saints Row 2\SR2_pc.exe")
print('='*74); print('SR2_pc.exe!0x7F4D60 (被汉化hook的原版)'); print('='*74)
rva=0x7F4D60-0x400000
for ins in md.disasm(data[r2o(rva):r2o(rva)+0x120], 0x7F4D60):
    print(f'  {ins.address:06X}: {ins.mnemonic:8s} {ins.op_str}')
    if ins.mnemonic=='ret': break

# DLL 0xAD1A0
pe,data,r2o=mk(r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.dll")
print('\n'+'='*74); print('DFEngine.dll!0xAD1A0 (查找函数)'); print('='*74)
for ins in md.disasm(data[r2o(0xAD1A0):r2o(0xAD1A0)+0x140], 0xAD1A0):
    print(f'  {ins.address:06X}: {ins.mnemonic:8s} {ins.op_str}')
    if ins.mnemonic=='ret': break
