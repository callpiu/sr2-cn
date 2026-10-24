# -*- coding: utf-8 -*-
"""搜索引擎内存中是否存在正确的字符表 (arr[i] = 该字符的码点)"""
import sys, struct, ctypes
from ctypes import wintypes
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0,'.')
from _vpp import Vpp
gv=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
def pc(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl=pc(gv.read(gv.find('charlist_CH')))
print('charlist', len(cl), 'cl[371]=', cl[371], chr(cl[371]), 'cl[0]=', cl[0])

k32=ctypes.WinDLL('kernel32', use_last_error=True)
h=k32.OpenProcess(0x0400|0x0010, False, 4296)
class MBI(ctypes.Structure):
    _fields_=[('BaseAddress',ctypes.c_void_p),('AllocationBase',ctypes.c_void_p),('AllocationProtect',wintypes.DWORD),
              ('RegionSize',ctypes.c_size_t),('State',wintypes.DWORD),('Protect',wintypes.DWORD),('Type',wintypes.DWORD)]
mbi=MBI()
# 特征: arr[0]=32, arr[1]=33, ... arr[94]=126, arr[95]=127 ... 太通用
# 用中段: arr[300..320] 的码点
sig = b''.join(struct.pack('<H', c) for c in cl[300:340])
print('sig len', len(sig), 'sample', cl[300:310])
buf=ctypes.create_string_buffer(8*1024*1024); got=ctypes.c_size_t(0)
hits=[]; addr=0; scanned=0
while addr<0x7FFFFFFF:
    if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        addr+=0x1000; continue
    base=mbi.BaseAddress or 0; size=mbi.RegionSize
    if mbi.State==0x1000 and not (mbi.Protect&0x100) and not (mbi.Protect&0x01) and size<0x8000000:
        off=0
        while off<size:
            n=min(len(buf), size-off)
            if k32.ReadProcessMemory(h, ctypes.c_void_p(base+off), buf, n, ctypes.byref(got)) and got.value:
                dd=buf.raw[:got.value]; scanned+=got.value
                p=0
                while True:
                    p=dd.find(sig,p)
                    if p<0: break
                    hits.append(base+off+p-600); p+=1
                    if len(hits)>10: break
                off+=got.value
            else: off+=0x1000
    addr=base+size if size else addr+0x1000
print('scanned %.0fMB; correct-charlist sig hits: %d'%(scanned/1048576, len(hits)))
for a in hits[:10]:
    print('   candidate table base 0x%X'%a)
