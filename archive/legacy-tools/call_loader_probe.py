# -*- coding: utf-8 -*-
"""call_loader_probe.py —— 决定性实验：
1) 远程调用引擎加载器 0x7F4430，把 charlist 载入（当前 num_cchars=0）
2) 转储运行时字表，找出「你/的/弟/兄/们/需/要/保/护」的真实码点与字形索引
3) 对 9 个字符直接调用 compress_char(0x7F4F60)，得到真实 glyph

调用约定：加载器无参数（eax 由内部全局决定）。compress_char 用 __fastcall:
   ax = 输入码点, edi = 输出 flag 指针, 返回 ax = 字形索引
改用 stdcall shellcode 包装来保证正确。
"""
import sys, struct, ctypes, time
sys.path.insert(0, r"F:\sr2-cn")
sys.path.insert(0, r"F:\sr2-cn\_day_2026-10-07\02_诊断脚本")
sys.stdout.reconfigure(encoding="utf-8")
from a5_common import Target, k32, wintypes

t = Target(writable=True)
print("=" * 78)
p = t.read_u32(t.va(0x2528B2C))
n = t.read_u32(t.va(0x2528B30))
print("调用前: charlist=0x%08X  num_cchars=%d" % (p or 0, n or 0))

# --- 准备 shellcode: 调用 0x7F4430 (无参) ---
LOADER = t.va(0x7F4430)
# 简单 shellcode: int3 无关；直接 call 会返回。用 mov eax,addr; call eax; ret
sc = b"\xB8" + struct.pack("<I", LOADER) + b"\xFF\xD0" + b"\xC3"
code = t.alloc(0x1000, exec_ok=True)
print("shellcode @ 0x%08X (exec)" % code)
t.write(code, sc)

THREAD_PRIORITY = 0
k32.CreateRemoteThread.restype = wintypes.HANDLE
k32.CreateRemoteThread.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                   ctypes.c_size_t, ctypes.c_void_p,
                                   ctypes.c_void_p, wintypes.DWORD,
                                   ctypes.POINTER(wintypes.DWORD)]
hth = k32.CreateRemoteThread(t.h, None, 0, ctypes.c_void_p(code), None, 0, None)
if not hth:
    print("CreateRemoteThread 失败 err=%d" % ctypes.get_last_error())
else:
    r = k32.WaitForSingleObject(hth, 8000)
    print("线程返回: 0x%X" % r)
    k32.CloseHandle(hth)

time.sleep(0.3)
p = t.read_u32(t.va(0x2528B2C))
n = t.read_u32(t.va(0x2528B30))
print("调用后: charlist=0x%08X  num_cchars=%d" % (p or 0, n or 0))
t.free(code, 0x1000)
