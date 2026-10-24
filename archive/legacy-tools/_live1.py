# -*- coding: utf-8 -*-
"""Immediate memory probe of running SR2_pc.exe: find the charlist + static_CH copies."""
import ctypes, struct, sys, time, subprocess, re
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

k32 = ctypes.WinDLL('kernel32', use_last_error=True)

class MBI(ctypes.Structure):
    _fields_ = [('BaseAddress', ctypes.c_void_p), ('AllocationBase', ctypes.c_void_p),
                ('AllocationProtect', ctypes.c_uint32), ('__pad', ctypes.c_uint32),
                ('RegionSize', ctypes.c_size_t), ('State', ctypes.c_uint32),
                ('Protect', ctypes.c_uint32), ('Type', ctypes.c_uint32)]

def pid_of(name):
    out = subprocess.run(['tasklist', '/fo', 'csv', '/nh'], capture_output=True).stdout.decode('utf-8', 'replace')
    for line in out.splitlines():
        if line.lower().startswith('"%s"' % name.lower()):
            return int(line.split('","')[1])
    return None

pid = pid_of('SR2_pc.exe')
print("pid", pid)
if not pid:
    sys.exit(0)
h = k32.OpenProcess(0x1F0FFF, False, pid)
if not h:
    print("OpenProcess failed", ctypes.get_last_error()); sys.exit(1)

SIGS = {
    'CLTXT':  b'//Used character list',
    'CNT':    b'count=',
    'SUB':    bytes.fromhex('f284ed870193074c005b0066'),
    'U16':    '你的弟兄们需要你的保护'.encode('utf-16-le'),
    'FNT':    b'fnt_chinese.peg',
    'VF3':    struct.pack('<IIII', 1, 32, 63, 94),
}
hits = {k: [] for k in SIGS}
addr, total, t0 = 0, 0, time.time()
mbi = MBI()
while addr < 0x7FFFFFFFFFFF:
    if k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
        break
    base, size = mbi.BaseAddress or 0, mbi.RegionSize
    prot = mbi.Protect & 0xFF
    if mbi.State == 0x1000 and prot in (0x02, 0x04, 0x06, 0x20, 0x40, 0x80) and 0 < size <= 512*1024*1024:
        buf = ctypes.create_string_buffer(size)
        n = ctypes.c_size_t(0)
        if k32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, size, ctypes.byref(n)) and n.value:
            total += n.value
            d = buf.raw[:n.value]
            for k, pat in SIGS.items():
                st = 0
                while len(hits[k]) < 40:
                    i = d.find(pat, st)
                    if i < 0: break
                    hits[k].append((base + i, d, i))
                    st = i + 1
    addr = base + size
print("scanned %.0f MB in %.0fs" % (total/1e6, time.time()-t0))
for k in SIGS:
    print("%-6s hits=%d" % (k, len(hits[k])))
k32.CloseHandle(h)

# dump contexts
out = open(r'F:\sr2-cn\_probe_live.txt', 'w', encoding='utf-8')
def w(*a):
    s = ' '.join(str(x) for x in a)
    print(s); out.write(s+'\n'); out.flush()

for addr0, d, i in hits['CLTXT'][:3]:
    w("=== CLTXT @0x%X ===" % addr0)
    w(repr(d[i:i+400]))
for addr0, d, i in hits['CNT'][:10]:
    w("=== CNT @0x%X : %r" % (addr0, d[max(0,i-60):i+60]))
for addr0, d, i in hits['SUB'][:3]:
    w("=== SUB @0x%X ===" % addr0)
    o = i + 4; sl = []
    for _ in range(40):
        v = struct.unpack_from('>H', d, o)[0]; o += 2
        if v == 0: break
        sl.append(v)
    w("  slots:", sl)
for addr0, d, i in hits['U16'][:3]:
    w("=== U16 plaintext @0x%X : %r" % (addr0, d[max(0,i-40):i+80]))
for addr0, d, i in hits['FNT'][:5]:
    w("=== FNT name @0x%X : %r" % (addr0, d[max(0,i-30):i+40]))
for addr0, d, i in hits['VF3'][:5]:
    w("=== VF3 UV head @0x%X : %r" % (addr0, d[max(0,i-16):i+48].hex(' ')))
w("DONE")
out.close()
