# -*- coding: utf-8 -*-
import pefile
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
pe=pefile.PE(G+'/SR2_pc.exe', fast_load=True)
print("ImageBase =", hex(pe.OPTIONAL_HEADER.ImageBase))
print("节区:")
for s in pe.sections:
    nm=s.Name.rstrip(b'\x00').decode('latin1','replace')
    print("  %-10s VA=0x%08X VS=%d RA=0x%08X RS=%d" % (nm, s.VirtualAddress, s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData))
