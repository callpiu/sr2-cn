# -*- coding: utf-8 -*-
import sys, struct
sys.path.insert(0,'F:/sr2-cn')
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
for fn in ['juiced_CH.le_strings','juiced_CZ.le_strings']:
    raw=open(G+r'\Mods\JUICED - Strings\\'+fn,'rb').read()
    print("=== %s (%d bytes) ===" % (fn,len(raw)))
    for off in range(0,min(len(raw),160),16):
        c=raw[off:off+16]
        print("  %04X  %-47s  %s" % (off, c.hex(' ').upper(),
              "".join(chr(b) if 32<=b<127 else '.' for b in c)))
    m,ver,bk,cnt=struct.unpack_from('<IHHI',raw,0)
    print("  magic=0x%08X ver=%d buckets=%d count=%d" % (m,ver,bk,cnt))
    print()
