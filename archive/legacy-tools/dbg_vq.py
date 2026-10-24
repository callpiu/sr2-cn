import ctypes
from ctypes import wintypes, byref, sizeof
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
P_SZ = ctypes.POINTER(ctypes.c_size_t)

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wintypes.DWORD), ("RegionSize", ctypes.c_size_t),
                ("State", wintypes.DWORD), ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

VQ = k32.VirtualQueryEx
VQ.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
VQ.restype = ctypes.c_size_t
OP = k32.OpenProcess
OP.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
OP.restype = wintypes.HANDLE

pid = __import__("os").getpid()
h = OP(0x0010 | 0x0400, False, pid)
print("handle:", h, "sizeof(MBI)=", sizeof(MBI))
mbi = MBI()
for addr in (0x10000, 0x160208C0000):
    r = VQ(h, ctypes.c_void_p(addr), byref(mbi), sizeof(mbi))
    print("addr=%#x ret=%d err=%d base=%s allocbase=%s regionsize=%#x state=%#x protect=%#x type=%#x" % (
        addr, r, ctypes.get_last_error(),
        hex(mbi.BaseAddress or 0), hex(mbi.AllocationBase or 0), mbi.RegionSize, mbi.State, mbi.Protect, mbi.Type))
k32.CloseHandle(h)
