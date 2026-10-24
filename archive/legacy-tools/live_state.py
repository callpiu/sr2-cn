# -*- coding: utf-8 -*-
"""live_state.py - 读实时 charlist 状态 + 转储完整运行时字表。
只读，不写内存。"""
import sys, struct, ctypes
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import ce_mini as C

h = C.open_process(C.find_pid())
print("pid =", C.find_pid())

def rd(addr, n):
    return C.read_mem(h, addr, n)

def u32(addr):
    b = rd(addr, 4)
    return struct.unpack("<I", b)[0] if b else None

p = u32(0x2528B2C)
n = u32(0x2528B30)
print("charlist ptr = 0x%08X" % (p or 0))
print("num_cchars   = %s" % n)

# 第二对 / 标志
for va, nm in [(0x2528B28, "foreign_flag"), (0x2528B29, "flag29"), (0x2528B2A, "flag2a"),
               (0x2528B34, "ptr2"), (0x2528B38, "cnt2"), (0x2528B48, "g_b48")]:
    b = rd(va, 4)
    print("  [0x%08X] %-13s = %s" % (va, nm, b.hex(" ") if b else "?"))

if p and n:
    raw = rd(p, min(n, 4096) * 4)
    if raw:
        arr = struct.unpack("<%dI" % (len(raw) // 4), raw[:len(raw)//4*4])
        print("\n=== 运行时字表前 40 项 (cp / glyph) ===")
        for i in range(min(40, len(arr))):
            lo = arr[i] & 0xFFFF
            hi = (arr[i] >> 16) & 0xFFFF
            print("  [%4d] cp=0x%04X %-3s glyph=%d" % (
                i, lo, chr(lo) if 32 <= lo < 0xFFFF else "?", hi))
else:
    print("\n!! 字表未加载")
C.k32.CloseHandle(h)
