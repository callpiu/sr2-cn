import ctypes, subprocess, struct, sys
out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True).stdout.decode("utf-8", "replace")
pid = next((int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"sr2_pc.exe"')), None)
print("pid =", pid)
if not pid: sys.exit(0)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
h = k32.OpenProcess(0x1F0FFF, False, pid)

class MBI(ctypes.Structure):
    _fields_ = [('BaseAddress', ctypes.c_void_p), ('AllocationBase', ctypes.c_void_p),
                ('AllocationProtect', ctypes.c_uint32), ('__pad', ctypes.c_uint32),
                ('RegionSize', ctypes.c_size_t), ('State', ctypes.c_uint32),
                ('Protect', ctypes.c_uint32), ('Type', ctypes.c_uint32)]
mbi = MBI()
addr = 0
found = []
while addr < 0x7FFFFFFFFFFF:
    if k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
        break
    base, size = mbi.BaseAddress or 0, mbi.RegionSize
    prot = mbi.Protect & 0xFF
    if mbi.State == 0x1000 and prot in (0x02, 0x04, 0x06, 0x20, 0x40, 0x80) and 0 < size <= 512*1024*1024:
        buf = ctypes.create_string_buffer(size); got = ctypes.c_size_t(0)
        if k32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, size, ctypes.byref(got)) and got.value:
            d = buf.raw[:got.value]
            st = 0
            while True:
                i = d.find(b"VFNT", st)
                if i < 0: break
                st = i + 1
                if i + 0x90 <= len(d):
                    N = struct.unpack_from("<I", d, i + 8)[0]
                    w = struct.unpack_from("<I", d, i + 0x0C)[0]
                    hh = struct.unpack_from("<I", d, i + 0x10)[0]
                    nm = d[i+0x28:i+0x28+40].split(b"\x00")[0]
                    tga = d[i+0x68:i+0x68+40].split(b"\x00")[0]
                    if 0 < N < 20000 and w < 8192 and hh < 8192:
                        found.append((base + i, N, w, hh, nm.decode("latin-1"), tga.decode("latin-1")))
    addr = base + size
print("内存中找到 %d 个 VFNT" % len(found))
for a, N, w, hh, nm, tga in sorted(found):
    print("  0x%08X  N=%-5d %dx%-5d  %-22s %s" % (a, N, w, hh, nm, tga))

print("\n--- 字体对象表 0x234F268 前 12 项 ---")
for i in range(12):
    b = ctypes.create_string_buffer(4); got = ctypes.c_size_t(0)
    if k32.ReadProcessMemory(h, ctypes.c_void_p(0x234F268 + i*4), b, 4, ctypes.byref(got)):
        v = struct.unpack("<I", b.raw[:4])[0]
        print("  [%d] = 0x%08X" % (i, v))
k32.CloseHandle(h)
