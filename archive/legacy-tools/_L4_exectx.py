# -*- coding: utf-8 -*-
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
raw=open(G+'/SR2_pc.exe','rb').read()
def dump(off, n=80):
    s=raw[off:off+n]
    # 截到第一个 \0
    z=s.find(b'\x00')
    if z>=0: s=s[:z]
    print("  0x%08X: %r" % (off, s))
print("=== 0xA26020 区域（格式串表）===")
for base in range(0xA26000, 0xA260B0, 0x10):
    dump(base, 16)
print("\n=== 0xA0C660 附近（voice_script）===")
for base in range(0xA0C640, 0xA0C6C0, 0x10):
    dump(base, 16)
print("\n=== 0xAD3F10 / 0xADC2BA（另两处 static_）===")
dump(0xAD3F00, 32); dump(0xADC2A0, 48)
