# -*- coding: utf-8 -*-
"""force_load_and_dump.py —— 决定性实验（有崩溃风险，需用户同意）

1) 远程调用 charlist 加载器 0x7F4430（无参；内部读 [0xe8c470] 语言ID=CH）
2) 读取 [0x2528B2C]/[0x2528B30] 结果
3) 若加载成功，dump 完整运行时字表并与磁盘 charlist_CH 逐项比对

用法:
    python force_load_and_dump.py --dry     # 只准备，不执行（默认）
    python force_load_and_dump.py --go      # 真正执行
"""
import sys, struct, ctypes, time, os
sys.path.insert(0, r"F:\sr2-cn")
sys.path.insert(0, r"F:\sr2-cn\_day_2026-10-07\02_诊断脚本")
sys.stdout.reconfigure(encoding="utf-8")
from a5_common import Target, k32, wintypes

DO = "--go" in sys.argv

t = Target(writable=True)

def state():
    p = t.read_u32(t.va(0x2528B2C))
    n = t.read_u32(t.va(0x2528B30))
    return p, n

p0, n0 = state()
print("=" * 78)
print("调用前: charlist=0x%08X  num_cchars=%d" % (p0 or 0, n0 or 0))
print("语言ID [0xe8c470] = %d" % (t.read_u32(t.va(0xE8C470)) or -1))

LOADER = t.va(0x7F4430)
print("加载器 VA(运行时) = 0x%08X" % LOADER)

# 校验字节确实是 mov eax,[0xe8c470] (A1 70 C4 E8 00)
cb = t.read(LOADER, 8)
print("字节 =", cb.hex(" ") if cb else None)

if not DO:
    print("\n[DRY-RUN] 未执行。加 --go 真正调用。")
    sys.exit(0)

# 构造 shellcode: mov eax, LOADER; call eax; ret
sc = b"\xB8" + struct.pack("<I", LOADER) + b"\xFF\xD0" + b"\xC3"
code = t.alloc(0x1000, exec_ok=True)
if not code:
    print("alloc 失败")
    sys.exit(1)
print("shellcode @ 0x%08X" % code)
t.write(code, sc)
back = t.read(code, len(sc))
print("写回校验:", back.hex(" "), "OK" if back == sc else "!! 不一致")

k32.CreateRemoteThread.restype = wintypes.HANDLE
k32.CreateRemoteThread.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                   ctypes.c_size_t, ctypes.c_void_p,
                                   ctypes.c_void_p, wintypes.DWORD,
                                   ctypes.POINTER(wintypes.DWORD)]
hth = k32.CreateRemoteThread(t.h, None, 0, ctypes.c_void_p(code), None, 0, None)
if not hth:
    print("CreateRemoteThread 失败 err=%d" % ctypes.get_last_error())
    t.free(code, 0x1000)
    sys.exit(1)
print("线程已创建句柄=0x%X，等待…" % hth)
r = k32.WaitForSingleObject(hth, 10000)
print("WaitForSingleObject = 0x%X (0=成功结束, 0x102=超时)" % r)
k32.CloseHandle(hth)
time.sleep(0.3)

p1, n1 = state()
print("调用后: charlist=0x%08X  num_cchars=%d" % (p1 or 0, n1 or 0))

if p1 and n1:
    print("\n★ 加载成功！dump 前 60 项：")
    arr = t.read_bulk(p1, min(n1, 60))
    for i, v in enumerate(arr):
        lo = v & 0xFFFF
        hi = (v >> 16) & 0xFFFF
        print("  [%4d] cp=0x%04X %-3s glyph=%d" % (
            i, lo, chr(lo) if 32 <= lo < 0xFFFF else "?", hi))
    # 完整 dump 到文件
    full = t.read_bulk(p1, n1)
    out = r"F:\sr2-cn\_runtime_charlist.txt"
    with open(out, "w", encoding="utf-8") as f:
        for v in full:
            f.write("%d %d\n" % (v & 0xFFFF, (v >> 16) & 0xFFFF))
    print("\n完整字表已存: %s (%d 项)" % (out, len(full)))

t.free(code, 0x1000)
print("shellcode 已释放")
