# -*- coding: utf-8 -*-
"""运行时内存探针 v2：搜索引擎实际持有的字符表与字体对象"""
import sys, struct, ctypes, time
from ctypes import wintypes
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(GAME)
def parse_charlist(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl = parse_charlist(gv.read(gv.find('charlist_CH')))
atlas = vf3 = None
for e in gv.entries():
    if e['name']=='fnt_chinese':
        d=gv.read(e)
        if len(d)==4194304: atlas=d
        else: vf3=d

SIGS = {}
# 1) charlist 前 80 项的 u16 LE 数组
SIGS['CL_U16'] = b''.join(struct.pack('<H', c) for c in cl[:80])
# 2) charlist 文本形态
SIGS['CL_TXT'] = b'32\n33\n34\n35\n36\n37\n38\n39\n'
# 3) vf3 头 32 字节（作者版）
SIGS['VF3_HDR'] = vf3[:32]
# 4) 图集开头 32 字节
SIGS['ATLAS'] = atlas[:32]
# 5) exe 字符串
SIGS['CLTXT'] = b'//Used character list'

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
PAGE_NOACCESS = 0x01

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [('BaseAddress', ctypes.c_void_p), ('AllocationBase', ctypes.c_void_p),
                ('AllocationProtect', wintypes.DWORD), ('RegionSize', ctypes.c_size_t),
                ('State', wintypes.DWORD), ('Protect', wintypes.DWORD), ('Type', wintypes.DWORD)]

pid = 4296
h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
print('handle', h, 'pid', pid, flush=True)
if not h:
    print('OpenProcess failed', ctypes.get_last_error()); sys.exit(1)

mbi = MEMORY_BASIC_INFORMATION()
addr = 0
maxaddr = 0x7FFFFFFF
results = {k: [] for k in SIGS}
scanned = 0
buf = ctypes.create_string_buffer(4*1024*1024)
read = ctypes.c_size_t(0)
t0 = time.time()
nregions = 0
while addr < maxaddr:
    if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        addr += 0x1000; continue
    base = mbi.BaseAddress or 0
    size = mbi.RegionSize
    if mbi.State == MEM_COMMIT and not (mbi.Protect & PAGE_GUARD) and not (mbi.Protect & PAGE_NOACCESS):
        nregions += 1
        off = 0
        while off < size:
            n = min(len(buf), size-off)
            if k32.ReadProcessMemory(h, ctypes.c_void_p(base+off), buf, n, ctypes.byref(read)) and read.value:
                data = buf.raw[:read.value]
                scanned += read.value
                for name, sig in SIGS.items():
                    p = 0
                    while True:
                        p = data.find(sig, p)
                        if p < 0: break
                        if len(results[name]) < 8:
                            results[name].append(base+off+p)
                        p += 1
                off += read.value
            else:
                off += 0x1000
    addr = base + size if size else addr + 0x1000
print('scanned %.1f MB in %.1fs, regions=%d' % (scanned/1048576, time.time()-t0, nregions), flush=True)

out = open(r'F:\sr2-cn\_probe_live2.txt','w',encoding='utf-8')
for name in SIGS:
    out.write('=== %s : %d hits\n' % (name, len(results[name])))
    for a in results[name][:8]:
        out.write('   @0x%X\n' % a)
out.close()
print('done', flush=True)
