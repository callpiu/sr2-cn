# -*- coding: utf-8 -*-
"""dump 乱码串所在地址的上下文，判断它是什么结构"""
import sys, struct
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

C.enable_debug_privilege()
A = 0x3C28A164
h = C.open_process(C.find_pid())
print("目标进程 pid=%d" % C.find_pid())

raw = C.read_mem(h, A - 96, 512)
if raw is None:
    print("读取失败"); sys.exit(1)

print("\n=== 0x%X 前 96 字节 + 后 416 字节 ===" % A)
print("以 UTF-16LE 解读看看周围有没有别的中文：")
try:
    dec = raw.decode("utf-16-le", "replace")
    for i in range(0, len(dec), 32):
        seg = dec[i:i+32].replace("\x00", "·")
        print("   %04X  %s" % (A - 96 + i*2, seg))
except Exception as ex:
    print("err", ex)

print("\n=== 精确切片：命中处开始的 Unicode ===")
mid = raw[96:]
try:
    print("  LE  : %r" % mid[:80].decode("utf-16-le", "replace"))
except Exception:
    pass
print("  原始: %s" % raw[64:160].hex(" ").upper())

# 往前找可能的长度/结束：找 00 00
print("\n=== 从 0x%X 起向后找终止符 ===" % A)
for n in range(0, 120, 2):
    if raw[96+n:96+n+2] == b"\x00\x00":
        s = raw[96:96+n].decode("utf-16-le", "replace")
        print("  串长 %d 个 UTF-16 字符: %r" % (n//2, s))
        break

# 往前找该串的起点：往回扫直到非中文
print("\n=== 往回找串的起点 ===")
start = None
for back in range(2, 200, 2):
    two = raw[96-back:96-back+2]
    if two == b"\x00\x00":
        start = 96 - back + 2
        break
if start is not None:
    s = raw[start:96+120].decode("utf-16-le", "replace")
    print("  起点可能在 0x%X : %r" % (A - 96 + start, s[:120]))

C.k32.CloseHandle(h)
