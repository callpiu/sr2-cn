# -*- coding: utf-8 -*-
"""核实语言码表：0xDD1104（第六轮声称含CH）vs 0xA25FD8 区域。"""
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()

def dump_tab(off, n):
    print("=== 表 @0x%08X  (%d 个 dword 指针) ===" % (off, n))
    ptrs=[]
    for i in range(n):
        p=raw[off+i*4:off+i*4+4]
        v=int.from_bytes(p,'little')
        ptrs.append(v)
    for i,v in enumerate(ptrs):
        if v==0:
            print("  [%2d] 0x00000000  <NULL>" % i); continue
        if 0<v<len(raw):
            s=raw[v:raw.find(b'\x00',v)].decode('latin1')
            print("  [%2d] 0x%08X  %r" % (i,v,s))
        else:
            print("  [%2d] 0x%08X  (越界)" % (i,v))

dump_tab(0xDD1104, 16)
print()
dump_tab(0xDD10C4, 16)
