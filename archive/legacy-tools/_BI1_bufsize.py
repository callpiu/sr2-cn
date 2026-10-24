# -*- coding: utf-8 -*-
import sys, struct, ctypes
from ctypes import wintypes
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp
G = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(G)
def pc(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl=pc(gv.read(gv.find('charlist_CH')))
k32=ctypes.WinDLL('kernel32', use_last_error=True)
h=k32.OpenProcess(0x0400|0x0010, False, 4296)
class MBI(ctypes.Structure):
    _fields_=[('BaseAddress',ctypes.c_void_p),('AllocationBase',ctypes.c_void_p),('AllocationProtect',wintypes.DWORD),
              ('RegionSize',ctypes.c_size_t),('State',wintypes.DWORD),('Protect',wintypes.DWORD),('Type',wintypes.DWORD)]
mbi=MBI()
for a in (0x1F6CC80, 0x1F6CC80-64, 0x1F6CC80+6000):
    k32.VirtualQueryEx(h, ctypes.c_void_p(a), ctypes.byref(mbi), ctypes.sizeof(mbi))
    print('@0x%X base=0x%X size=0x%X state=0x%X prot=0x%X type=0x%X'%(a, mbi.BaseAddress or 0, mbi.RegionSize, mbi.State, mbi.Protect, mbi.Type))
def rd(a,n):
    b=ctypes.create_string_buffer(n); got=ctypes.c_size_t(0)
    if k32.ReadProcessMemory(h, ctypes.c_void_p(a), b, n, ctypes.byref(got)): return b.raw[:got.value]
    return None
d=rd(0x1F6CC80-32, 32)
print('pre :', d.hex() if d else None)
d=rd(0x1F6CC80+446, 64)
print('@+446:', d.hex() if d else None)
print('         as u16:', struct.unpack('<32H', d) if d else None)
# 搜索文件后续值
for name,seq in [('items224-231', cl[224:232]), ('items224-255', cl[224:256])]:
    sig=b''.join(struct.pack('<H',c) for c in seq)
    hits=[]; addr=0
    buf=ctypes.create_string_buffer(4*1024*1024); got=ctypes.c_size_t(0); scanned=0
    while addr<0x7FFFFFFF:
        if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            addr+=0x1000; continue
        base=mbi.BaseAddress or 0; size=mbi.RegionSize
        if mbi.State==0x1000 and not (mbi.Protect&0x100) and not (mbi.Protect&0x01):
            off=0
            while off<size:
                n=min(len(buf),size-off)
                if k32.ReadProcessMemory(h, ctypes.c_void_p(base+off), buf, n, ctypes.byref(got)) and got.value:
                    dd=buf.raw[:got.value]; scanned+=got.value
                    p=0
                    while True:
                        p=dd.find(sig,p)
                        if p<0: break
                        hits.append(base+off+p); p+=1
                        if len(hits)>6: break
                    off+=got.value
                else: off+=0x1000
        addr=base+size if size else addr+0x1000
    print(f'{name}: hits={len(hits)} {[hex(x) for x in hits[:6]]} (scanned {scanned/1048576:.0f}MB)')
