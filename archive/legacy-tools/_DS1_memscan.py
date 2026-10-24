import ctypes, ctypes.wintypes as w, subprocess, sys, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
out = subprocess.run(["tasklist","/fo","csv","/nh"],capture_output=True).stdout.decode("utf-8","replace")
pid = next((int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"sr2_pc.exe"')), None)
print("pid =", pid)
if not pid: sys.exit(0)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
h = k32.OpenProcess(0x1F0FFF, False, pid)
MEM_COMMIT=0x1000; PAGE_READWRITE=4; PAGE_EXECUTE_READWRITE=0x40; PAGE_READONLY=2
class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_=[("BaseAddress",ctypes.c_void_p),("AllocationBase",ctypes.c_void_p),
              ("AllocationProtect",w.DWORD),("__align1",w.DWORD),("RegionSize",ctypes.c_size_t),
              ("State",w.DWORD),("Protect",w.DWORD),("Type",w.DWORD),("__align2",w.DWORD)]
def getat(p,name,ext):
    v=Vpp(p); return v.read(v.find(name,ext))
G=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
mine = getat(os.path.join(G,"patch.vpp_pc"),"fnt_chinese","g_peg_pc")
offi = getat(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","fnt_chinese","g_peg_pc")
sig_m = mine[0x10000:0x10100]
sig_o = offi[0x10000:0x10100]
print("搜特征: 我的图集[0x10000:0x10100] / 官方图集[0x10000:0x10100]")
addr=0; maxaddr=0x80000000
mbi=MEMORY_BASIC_INFORMATION(); sz=ctypes.sizeof(mbi)
hits_m=[]; hits_o=[]; scanned=0
while addr < maxaddr:
    r=k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), sz)
    if not r: break
    base=mbi.BaseAddress or 0; rsz=mbi.RegionSize or 0
    if mbi.State==MEM_COMMIT and mbi.Protect in (PAGE_READWRITE,PAGE_EXECUTE_READWRITE,PAGE_READONLY) and rsz < 0x8000000:
        buf=ctypes.create_string_buffer(rsz); got=ctypes.c_size_t(0)
        if k32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, rsz, ctypes.byref(got)):
            d=buf.raw[:got.value]; scanned+=len(d)
            if sig_m in d: hits_m.append((hex(base), d.find(sig_m)))
            if sig_o in d: hits_o.append((hex(base), d.find(sig_o)))
    addr = base + rsz
    if rsz==0: break
print("已扫描 %d MB" % (scanned>>20))
print("我的图集命中:", hits_m[:5])
print("官方图集命中:", hits_o[:5])
