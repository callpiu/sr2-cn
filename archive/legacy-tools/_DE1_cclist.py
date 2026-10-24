import ctypes, ctypes.wintypes as w, subprocess, struct, sys
out = subprocess.run(["tasklist","/fo","csv","/nh"],capture_output=True).stdout.decode("utf-8","replace")
pid = next((int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"sr2_pc.exe"')), None)
print("pid =", pid)
if not pid: sys.exit(0)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
h = k32.OpenProcess(0x1F0FFF, False, pid)
if not h: print("OpenProcess fail", ctypes.get_last_error()); sys.exit(1)
def rd(a,n):
    b=ctypes.create_string_buffer(n); g=ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(a), b, n, ctypes.byref(g)): return None
    return b.raw[:g.value]
def u32(a):
    b=rd(a,4); return struct.unpack("<I",b)[0] if b and len(b)==4 else None
pl=u32(0x02528B2C); nc=u32(0x02528B30)
print("cc_list=%s num_cchars=%d" % (hex(pl) if pl else pl, nc))
if not (pl and nc): sys.exit(0)
raw = rd(pl, nc*4)
open(r"F:/sr2-cn/_cc_list.bin","wb").write(raw)
print("dumped %d bytes -> _cc_list.bin" % len(raw))
rows=[struct.unpack_from("<HH",raw,i*4) for i in range(nc)]
off=[c-i for i,(u,c) in enumerate(rows)]
from collections import Counter
print("\ncompressed - index 的分布:", Counter(off).most_common(10))
for i in (0,1,50,95,223,233,300,371,403,1035,1836,2794):
    if i<nc: print("  idx=%4d unicode=U+%04X compressed=%5d  off=%d" % (i, rows[i][0], rows[i][1], off[i]))
k32.CloseHandle(h)
