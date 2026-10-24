import ctypes, ctypes.wintypes as w, subprocess, struct, sys

out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True).stdout.decode("utf-8", "replace")
pid = next((int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"sr2_pc.exe"')), None)
print("pid =", pid)
if not pid: sys.exit(0)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
h = k32.OpenProcess(0x1F0FFF, False, pid)
if not h: print("OpenProcess fail", ctypes.get_last_error()); sys.exit(1)

def rd(addr, n):
    buf = ctypes.create_string_buffer(n); got = ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, n, ctypes.byref(got)):
        return None
    return buf.raw[:got.value]

def u32(addr):
    b = rd(addr, 4)
    return struct.unpack("<I", b)[0] if b and len(b) == 4 else None

CHARLIST_PTR = 0x02528B2C
NUM_CCHARS   = 0x02528B30
LANG         = 0x00E8C470

pl = u32(CHARLIST_PTR); nc = u32(NUM_CCHARS); lg = u32(LANG)
print("LANG [0xE8C470]        = %s" % lg)
print("cc_list [0x2528B2C]    = %s" % (hex(pl) if pl else pl))
print("num_cchars [0x2528B30] = %s" % nc)

if pl and nc:
    print("\n--- cc_list 前 12 项 (u16 unicode, u16 compressed) ---")
    for i in range(min(12, nc)):
        b = rd(pl + i * 4, 4)
        if b and len(b) == 4:
            u, c = struct.unpack("<HH", b)
            print("  [%3d] unicode=U+%04X (%s)  compressed=%d" % (i, u, chr(u) if 32 <= u < 0x3000 or u < 0x2000 else "?", c))
    print("\n--- 关键项抽查 ---")
    for i in (95, 147, 336, 371, 1035, 1612, 1836, 2667, 2794):
        if i >= nc: continue
        b = rd(pl + i * 4, 4)
        if b and len(b) == 4:
            u, c = struct.unpack("<HH", b)
            print("  idx=%4d  unicode=U+%04X  compressed=%d  slot=idx+32=%d" % (i, u, c, i + 32))
    print("\n--- 表尾 ---")
    for i in range(max(0, nc - 4), nc):
        b = rd(pl + i * 4, 4)
        if b and len(b) == 4:
            u, c = struct.unpack("<HH", b)
            print("  idx=%4d  unicode=U+%04X  compressed=%d" % (i, u, c))
k32.CloseHandle(h)
