# -*- coding: utf-8 -*-
import re, pefile
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/DFEngine.dll','rb').read()
print("DFEngine.dll size =", len(raw))
pe=pefile.PE(G+'/DFEngine.dll', fast_load=True)
print("ImageBase =", hex(pe.OPTIONAL_HEADER.ImageBase))
for s in pe.sections:
    nm=s.Name.rstrip(b'\x00').decode('latin1','replace')
    print("  %-10s VA=0x%08X RA=0x%08X" % (nm, s.VirtualAddress, s.PointerToRawData))
print()
# 关键字符串
for pat in [b'ForceLanguage', b'charlist', b'le_strings', b'static_', b'voice_script',
            b'platform_', b'fnt_chinese', b'fnt_', b'Language', b'language',
            b'.txt', b'\xb0\xd7', b'CN', b'CH']:
    idxs=[m.start() for m in re.finditer(re.escape(pat), raw)]
    print("%-16s %d 次 %s" % (repr(pat), len(idxs), [hex(i) for i in idxs[:8]]))
