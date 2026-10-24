# -*- coding: utf-8 -*-
"""读取引擎内存中的字符表，与磁盘文件逐项对比"""
import sys, struct, ctypes
from ctypes import wintypes
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp
G = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(G)
def parse_charlist(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl_file = parse_charlist(gv.read(gv.find('charlist_CH')))
print('file charlist items', len(cl_file))

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
h = k32.OpenProcess(0x0400|0x0010, False, 4296)
print('handle', h)
def rd(addr, n):
    b = ctypes.create_string_buffer(n)
    got = ctypes.c_size_t(0)
    if k32.ReadProcessMemory(h, ctypes.c_void_p(addr), b, n, ctypes.byref(got)):
        return b.raw[:got.value]
    return None

addrs = [0x1F6CC80, 0x2370EC8, 0x2370FC8, 0x23712D8, 0x23713D8, 0x23716E8, 0x23717E8, 0x2371AF8]
N = 2795
for a in addrs:
    d = rd(a, N*2)
    if d is None:
        print('0x%X read FAIL' % a); continue
    vals = list(struct.unpack('<%dH' % N, d))
    diffs = [i for i in range(N) if vals[i] != cl_file[i]]
    print('0x%X  first20=%s  diffs=%d' % (a, vals[:20], len(diffs)))
    if diffs:
        print('     first diffs:', [(i, cl_file[i], vals[i]) for i in diffs[:12]])
    else:
        print('     IDENTICAL to file charlist')

# 顺便：搜索字符表中段的签名，确认是否还有别的副本
sig = b''.join(struct.pack('<H', c) for c in cl_file[1000:1100])
print('\nsearching mid-charlist signature len', len(sig))
k32.VirtualQueryEx.restype = ctypes.c_size_t
class MBI(ctypes.Structure):
    _fields_=[('BaseAddress',ctypes.c_void_p),('AllocationBase',ctypes.c_void_p),('AllocationProtect',wintypes.DWORD),
              ('RegionSize',ctypes.c_size_t),('State',wintypes.DWORD),('Protect',wintypes.DWORD),('Type',wintypes.DWORD)]
mbi=MBI(); addr=0; hits=[]; scanned=0
buf=ctypes.create_string_buffer(4*1024*1024); got=ctypes.c_size_t(0)
while addr < 0x7FFFFFFF:
    if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        addr+=0x1000; continue
    base=mbi.BaseAddress or 0; size=mbi.RegionSize
    if mbi.State==0x1000 and not (mbi.Protect & 0x100) and not (mbi.Protect & 0x01):
        off=0
        while off<size:
            n=min(len(buf), size-off)
            if k32.ReadProcessMemory(h, ctypes.c_void_p(base+off), buf, n, ctypes.byref(got)) and got.value:
                dd=buf.raw[:got.value]; scanned+=got.value
                p=0
                while True:
                    p=dd.find(sig,p)
                    if p<0: break
                    hits.append(base+off+p-2000)  # 回推 1000 项
                    p+=1
                off+=got.value
            else: off+=0x1000
    addr = base+size if size else addr+0x1000
print('scanned %.0f MB; mid-sig hits: %d'%(scanned/1048576, len(hits)))
for a in hits[:8]:
    d=rd(a, N*2)
    if d:
        vals=list(struct.unpack('<%dH'%N,d))
        diffs=[i for i in range(N) if vals[i]!=cl_file[i]]
        print('  @0x%X diffs=%d first20=%s'%(a,len(diffs),vals[:20]))
