# -*- coding: utf-8 -*-
"""Runtime probe: locate in-memory static_CH record + vf3 U/V array of SR2_pc.exe."""
import ctypes, ctypes.wintypes as wt, struct, sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
PAGE_READABLE = {0x02, 0x04, 0x06, 0x20, 0x40, 0x80}

class MBI(ctypes.Structure):
    _fields_ = [('BaseAddress', ctypes.c_void_p), ('AllocationBase', ctypes.c_void_p),
                ('AllocationProtect', ctypes.c_uint32), ('__pad', ctypes.c_uint32),
                ('RegionSize', ctypes.c_size_t), ('State', ctypes.c_uint32),
                ('Protect', ctypes.c_uint32), ('Type', ctypes.c_uint32)]

def pid_of(name):
    import subprocess
    out = subprocess.run(['tasklist', '/fo', 'csv', '/nh'], capture_output=True).stdout.decode('utf-8', 'replace')
    for line in out.splitlines():
        if line.lower().startswith('"%s"' % name.lower()):
            return int(line.split('","')[1])
    return None

def scan(pid, patterns):
    """yield (addr, pat_index, m) for each pattern found"""
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        raise OSError('OpenProcess failed %d' % ctypes.get_last_error())
    addr = 0
    hits = []
    mbi = MBI()
    total = 0
    while addr < 0x7FFFFFFFFFFF:
        if k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break
        base, size = mbi.BaseAddress or 0, mbi.RegionSize
        if mbi.State == MEM_COMMIT and (mbi.Protect in PAGE_READABLE) and 0 < size <= 256*1024*1024:
            buf = ctypes.create_string_buffer(size)
            n = ctypes.c_size_t(0)
            if k32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, size, ctypes.byref(n)) and n.value:
                total += n.value
                d = buf.raw[:n.value]
                for pi, pat in enumerate(patterns):
                    st = 0
                    while True:
                        i = d.find(pat, st)
                        if i < 0:
                            break
                        hits.append((base + i, pi))
                        st = i + 1
                        if len(hits) > 4000:
                            break
        addr = base + size
    k32.CloseHandle(h)
    return hits, total

# signatures
SIG_SUB = bytes.fromhex('f284ed87') + bytes([0x01, 0x93, 0x07, 0x4c, 0x00, 0x5b, 0x00, 0x66])
SIG_VF3_U0 = struct.pack('<III', 1, 32, 993)          # U[0],U[1],U[32]
SIG_VF3_UV = struct.pack('<IIIIII', 342, 156, 1427, 156, 404, 187)  # U/V[336],U/V[371],U/V[403]

TARGET = 'SR2_pc.exe'
print("waiting for", TARGET, "...")
pid = None
for _ in range(600):
    pid = pid_of(TARGET)
    if pid:
        break
    time.sleep(1)
if not pid:
    print("NOT RUNNING")
    sys.exit(1)
print("pid", pid, "- probing memory (this can take a minute) ...")
t0 = time.time()
hits, total = scan(pid, [SIG_SUB, SIG_VF3_U0, SIG_VF3_UV])
print("scanned %.1f MB in %.1fs" % (total/1e6, time.time()-t0))
for addr, pi in hits[:40]:
    print("  hit sig%d @ 0x%X" % (pi, addr))
print("total hits", len(hits))
