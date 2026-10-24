import ctypes, ctypes.wintypes as w, subprocess, struct, sys

out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True).stdout.decode("utf-8", "replace")
pid = next((int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"sr2_pc.exe"')), None)
print("pid =", pid)
if not pid: sys.exit(0)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
h = k32.OpenProcess(0x1F0FFF, False, pid)
if not h: print("fail"); sys.exit(1)

def rd(addr, n):
    buf = ctypes.create_string_buffer(n); got = ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, n, ctypes.byref(got)):
        return None
    return buf.raw[:got.value]

def u32(a):
    b = rd(a, 4)
    return struct.unpack("<I", b)[0] if b and len(b) == 4 else None

def f32(a):
    b = rd(a, 4)
    return struct.unpack("<f", b)[0] if b and len(b) == 4 else None

n = u32(0x252A5CC)
print("字体注册数 [0x252A5CC] =", n)
print("[0x252A5C8] =", hex(u32(0x252A5C8) or 0))
if n and n < 32:
    print("\n--- 字体表 @0x234F23C (handle, scale) ---")
    for i in range(n):
        hd = u32(0x234F23C + i * 8); sc = f32(0x234F23C + i * 8 + 4)
        print("  [%d] token=0x%08X handle=%s scale=%s" % (i, 0x80000001 + i, hex(hd) if hd else hd, sc))
        if hd and hd > 0x10000:
            b = rd(hd, 64)
            if b: print("        obj[0:64]= %s" % b.hex(" "))
print("\n--- 关键 token ---")
for nm, a in (("E98A7C thin", 0xE98A7C), ("E98A80", 0xE98A80), ("E98A6C", 0xE98A6C),
              ("E98A68", 0xE98A68), ("E98A90", 0xE98A90), ("E98A94", 0xE98A94), ("E98A98", 0xE98A98)):
    print("  %-12s = 0x%08X" % (nm, u32(a) or 0))
print("\n--- 字体名表 0xDE0FCC 起 ---")
b = rd(0xDE0FCC, 0xE0)
if b:
    for off in range(0, len(b) - 4, 4):
        e = b.find(b"\x00", off)
        if e > off:
            s = b[off:e]
            if all(32 <= c < 127 for c in s):
                print("  0x%08X  %s" % (0xDE0FCC + off, s.decode()))
k32.CloseHandle(h)
