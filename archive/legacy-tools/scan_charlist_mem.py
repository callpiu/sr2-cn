# -*- coding: utf-8 -*-
"""全内存结构扫描：找 charlist（u32 数组，低16位=码点）。
不依赖全局变量地址。"""
import ctypes, struct, sys, json
from ctypes import wintypes

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wintypes.HANDLE
k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.ReadProcessMemory.restype = wintypes.BOOL
k32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wintypes.DWORD), ("RegionSize", ctypes.c_size_t),
                ("State", wintypes.DWORD), ("Protect", wintypes.DWORD), ("Type", wintypes.DWORD)]

PID = 4868
h = k32.OpenProcess(0x001F0FFF, False, PID)
print("handle", h)

MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
PAGE_NOACCESS = 0x1
READABLE = {0x02, 0x04, 0x06, 0x08, 0x20, 0x40, 0x80}

def regions(maxbytes=0xFFF00000):
    addr = 0
    mbi = MBI()
    while addr < maxbytes:
        r = k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
        if not r: break
        base, size = mbi.BaseAddress or 0, mbi.RegionSize or 0
        if size == 0: break
        if mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in READABLE and not (mbi.Protect & PAGE_GUARD):
            yield base, size
        addr = base + size

def rd(a, n):
    b = (ctypes.c_ubyte * n)()
    g = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(a), b, n, ctypes.byref(g))
    return bytes(b) if ok and g.value == n else None

MINLEN = 1500
cands = []
total = 0
for base, size in regions():
    CH = 32 * 1024 * 1024
    off = 0
    tail = b""
    while off < size:
        n = min(CH, size - off)
        d = rd(base + off, n)
        if d is None:
            tail = b""
            off += n
            continue
        buf = tail + d
        total += len(buf)
        # 在 buf 里找候选：长度>=MINLEN 的 u32 串，lo 在 0x20..0xFFFE，升序比例>=0.75
        m = len(buf) // 4
        if m >= MINLEN:
            arr = struct.unpack("<%dI" % m, buf[:m*4])
            lo = [v & 0xFFFF for v in arr]
            hi = [v >> 16 for v in arr]
            # 滑窗找最优起点太慢，直接按 4 字节对齐逐点起评（限制数量）
            # 先整体评一次
            asc = sum(1 for i in range(m-1) if lo[i] < lo[i+1])
            frac = asc / (m-1)
            if frac >= 0.75 and all(0x20 <= x <= 0xFFFE for x in lo[:200]):
                cands.append((base + off - len(tail), m, frac, lo[:16], hi[:8]))
        tail = buf[-8:] if len(buf) >= 8 else buf
        off += n
    if len(cands) > 60: break

print("扫描字节总量 ~%.1f MB" % (total/1048576))
print("候选块 %d 个" % len(cands))
for a, m, frac, lo16, hi8 in cands[:40]:
    print("  @0x%08X len=%d 升序=%.3f lo=%s hi=%s" %
          (a, m, frac, " ".join("%04X" % x for x in lo16), " ".join("%04X" % x for x in hi8)))
