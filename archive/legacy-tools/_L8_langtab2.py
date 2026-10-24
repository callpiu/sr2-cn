# -*- coding: utf-8 -*-
"""修正：VA->文件偏移 = VA - 0x400000 (.text/.rdata 区段 VA==RA)"""
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
BASE=0x400000

def dump_tab(va, n):
    off=va-BASE
    print("=== 表 VA=0x%08X (off=0x%08X) ===" % (va, off))
    for i in range(n):
        v=int.from_bytes(raw[off+i*4:off+i*4+4],'little')
        if v==0:
            print("  [%2d] NULL" % i); continue
        fo=v-BASE
        if 0<fo<len(raw):
            s=raw[fo:raw.find(b'\x00',fo)].decode('latin1')
            print("  [%2d] VA=0x%08X off=0x%08X  %r" % (i,v,fo,s))
        else:
            print("  [%2d] VA=0x%08X (out)" % (i,v))

for va in (0xDD1104, 0xDD10C4, 0xDD1100, 0xDD1080, 0xDD1184):
    dump_tab(va, 16)
    print()
