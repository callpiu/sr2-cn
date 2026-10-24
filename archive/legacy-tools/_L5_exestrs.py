# -*- coding: utf-8 -*-
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
def strtab(start, end):
    i=start
    while i < end:
        j=raw.find(b'\x00', i)
        if j<0: break
        s=raw[i:j]
        if s:
            print("  0x%08X  %r" % (i, s))
        i=j+1
print("=== 0xA25FC0 .. 0xA26120 字符串表 ===")
strtab(0xA25FC0, 0xA26120)
