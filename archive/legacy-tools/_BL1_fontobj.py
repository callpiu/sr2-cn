# -*- coding: utf-8 -*-
import sys, struct, ctypes
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
k32=ctypes.WinDLL('kernel32', use_last_error=True)
h=k32.OpenProcess(0x0400|0x0010, False, 4296)
def rd(a,n):
    b=ctypes.create_string_buffer(n); got=ctypes.c_size_t(0)
    if k32.ReadProcessMemory(h, ctypes.c_void_p(a), b, n, ctypes.byref(got)): return b.raw[:got.value]
    return None
base=0x3A480420
d=rd(base-0x40, 0x200)
print('=== around vf3 hdr @0x%X ==='%base)
for i in range(0, len(d), 16):
    a=base-0x40+i
    row=d[i:i+16]
    asc=''.join(chr(c) if 32<=c<127 else '.' for c in row)
    print(' %08X %s  %s'%(a, row.hex(), asc))
print()
u=0x3A48B38C
d2=rd(u-0x60, 0x100)
print('=== around UV array @0x%X ==='%u)
for i in range(0, len(d2), 16):
    a=u-0x60+i
    row=d2[i:i+16]
    asc=''.join(chr(c) if 32<=c<127 else '.' for c in row)
    print(' %08X %s  %s'%(a, row.hex(), asc))
print()
# 看 vf3 头之后是否紧跟字符表/码点表
d3=rd(base, 0x1000)
print('vf3 hdr region first 0x100 bytes as u32:')
print(struct.unpack('<64I', d3[:256]))
