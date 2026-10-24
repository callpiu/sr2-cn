import ctypes, subprocess, struct, sys
out = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True).stdout.decode("utf-8", "replace")
pid = next((int(l.split('","')[1]) for l in out.splitlines() if l.lower().startswith('"sr2_pc.exe"')), None)
print("pid =", pid)
if not pid: sys.exit(0)
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
h = k32.OpenProcess(0x1F0FFF, False, pid)
def rd(a, n):
    buf = ctypes.create_string_buffer(n); got = ctypes.c_size_t(0)
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(a), buf, n, ctypes.byref(got)): return None
    return buf.raw[:got.value]

F = open(r"F:\sr2-cn\_fontdump\fnt_chinese.vf3_pc", "rb").read()
BASE = 0x3A480420
mem = rd(BASE, 0x120)
print("=== 内存 0x%X 起 0x120 字节 ===" % BASE)
for off in range(0, 0x120, 16):
    print("  +0x%03X  %s" % (off, mem[off:off+16].hex(" ")))
print("=== 文件 0x00 起 0x120 字节 ===")
for off in range(0, 0x120, 16):
    print("  +0x%03X  %s" % (off, F[off:off+16].hex(" ")))

# 逐字节找最长公共前缀
n = min(len(mem), len(F))
same = 0
for i in range(n):
    if mem[i] == F[i]: same = i + 1
    else: break
print("\n内存 vs 文件 相同前缀长度 = 0x%X (%d)" % (same, same))
print("首个不同: 文件[0x%X]=%02X  内存[0x%X]=%02X" % (same, F[same], same, mem[same]))
# 搜索 U 数组在内存中的位置
pat = struct.pack("<6I", 1, 32, 63, 94, 125, 156)
for a in range(BASE, BASE + 0x100000, 4):
    b = rd(a, 24)
    if b == pat:
        print("U 数组实际位置 = 0x%X  (文件偏移对应 0xAF6C → 差 %d)" % (a, a - BASE - 0xAF6C))
        break
k32.CloseHandle(h)
