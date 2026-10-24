# -*- coding: utf-8 -*-
"""在内存中搜索 '源索引 -> 字形索引' 映射表"""
import sys, struct, ctypes
from ctypes import wintypes
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
k32=ctypes.WinDLL('kernel32', use_last_error=True)
h=k32.OpenProcess(0x0400|0x0010, False, 4296)
class MBI(ctypes.Structure):
    _fields_=[('BaseAddress',ctypes.c_void_p),('AllocationBase',ctypes.c_void_p),('AllocationProtect',wintypes.DWORD),
              ('RegionSize',ctypes.c_size_t),('State',wintypes.DWORD),('Protect',wintypes.DWORD),('Type',wintypes.DWORD)]
mbi=MBI()

# 已知: charlist索引 -> 渲染出的字形索引
KNOWN = {332:362, 371:336, 391:354, 422:967, 1035:410, 1190:2342, 1836:1784, 2296:2268, 2667:2656}
# 也测试: 码点 -> 字形索引 (从 charlist 反查码点)
import sys as _s
_s.path.insert(0,'.')
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
KNOWN_CP = {cl[k]: v for k,v in KNOWN.items()}

buf=ctypes.create_string_buffer(8*1024*1024); got=ctypes.c_size_t(0)
def find_in(data, baseaddr, KN, results):
    # 以第一个键为锚
    keys = sorted(KN.keys())
    anchor = keys[0]; aval = KN[anchor]
    abytes = struct.pack('<H', aval)
    p=0
    while True:
        p = data.find(abytes, p)
        if p < 0: break
        A0 = baseaddr + p - anchor*2
        ok=True
        for k,v in KN.items():
            off = A0 + k*2 - baseaddr
            if off < 0 or off+2 > len(data) or struct.unpack_from('<H', data, off)[0] != v:
                ok=False; break
        if ok and len(results)<6:
            results.append(A0)
        p += 1

for name, KN in [('charlistIdx->glyph', KNOWN), ('codepoint->glyph', KNOWN_CP)]:
    results=[]
    addr=0; scanned=0
    while addr<0x7FFFFFFF:
        if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            addr+=0x1000; continue
        base=mbi.BaseAddress or 0; size=mbi.RegionSize
        if mbi.State==0x1000 and not (mbi.Protect&0x100) and not (mbi.Protect&0x01) and size < 0x4000000:
            off=0
            while off<size:
                n=min(len(buf), size-off)
                if k32.ReadProcessMemory(h, ctypes.c_void_p(base+off), buf, n, ctypes.byref(got)) and got.value:
                    find_in(buf.raw[:got.value], base+off, KN, results)
                    scanned+=got.value
                    off+=got.value
                else: off+=0x1000
        addr=base+size if size else addr+0x1000
    print(f'{name}: hits={len(results)} {[hex(x) for x in results]} (scanned {scanned/1048576:.0f}MB)', flush=True)
