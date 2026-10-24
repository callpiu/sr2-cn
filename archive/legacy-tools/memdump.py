import ctypes, ctypes.wintypes as wt, struct, sys
k=ctypes.WinDLL('kernel32', use_last_error=True)
PH=k.OpenProcess; PH.restype=wt.HANDLE
R=k.ReadProcessMemory; R.argtypes=[wt.HANDLE,wt.LPCVOID,wt.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
V=ctypes.wintypes.LPVOID
PID=int(sys.argv[1]); h=PH(PID,0x0010|0x0400,None)
if not h: print("OpenProcess 失败 err",ctypes.get_last_error()); sys.exit(1)
def read(addr,n):
    b=ctypes.create_string_buffer(n); got=ctypes.c_size_t()
    if not R(h,ctypes.c_void_p(addr),b,n,ctypes.byref(got)): return None
    return b.raw[:got.value]
def search(pat, region=0x10000, step=0x4000, limit=None):
    # 枚举进程主模块区域
    out=[]
    MEM=k.VirtualQueryEx; MEM.argtypes=[wt.HANDLE,wt.LPCVOID,wt.LPVOID,ctypes.c_size_t]
    VQ=ctypes.create_string_buffer(48)
    addr=0x10000; total=0
    while addr < 0x80000000:
        if not MEM(h,ctypes.c_void_p(addr),VQ,48): break
        q=ctypes.cast(VQ, ctypes.POINTER(wt.MEMORY_BASIC_INFORMATION)).contents
        base=int(q.BaseAddress); size=int(q.RegionSize)
        if q.State==0x1000 and q.Protect & 0x04 and size>0:
            data=read(base,size)
            if data:
                st=0
                while True:
                    i=data.find(pat,st)
                    if i<0: break
                    out.append(base+i); st=i+1
                    if len(out)>40: break
        addr=base+size
        if addr<base: break
        if limit and addr>limit: break
    return out
def seq(*slots): return b''.join(struct.pack('>H',s) for s in slots)
tests={
 'U数组(1,32,63,94..)': b''.join(struct.pack('<i',1+31*t) for t in range(8)),
 '辩护律师slot(内存)': seq(2506,1222,1089,1013),
 '辩护延师slot(内存)': seq(2506,1222,1057,1013),
 '斯蒂尔slot(内存)': seq(1379,2254,952,1601,1773),
}
for name,pat in tests.items():
    hits=search(pat)
    print("%-24s 命中 %d %s" % (name, len(hits), [hex(a) for a in hits[:6]]))
    if '辩护' in name and hits:
        a=hits[0]
        ctx=read(a-8, 32)
        print("      上下文:", ctx.hex(' '))
