# -*- coding: utf-8 -*-
"""运行时 hook 探测：
1) 枚举全部 32 位模块（含路径）
2) 确认 0x7F4430 hotpatch 桩
3) 找谁注入了 0x5B870000 那块 RWX 页（静态比对 shellcode 是否存在于某模块）
"""
import sys, struct, ctypes, ctypes.wintypes as wt, os
sys.stdout.reconfigure(encoding="utf-8")
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
psapi = ctypes.WinDLL("psapi", use_last_error=True)
PID = 4868
h = k32.OpenProcess(0x0400 | 0x0010, False, PID)


def rd(a, n):
    buf = (ctypes.c_char * n)()
    got = ctypes.c_size_t()
    k32.ReadProcessMemory(h, ctypes.c_void_p(a), buf, n, ctypes.byref(got))
    return buf.raw[: got.value]


arr = (wt.HMODULE * 2048)()
need = wt.DWORD()
psapi.EnumProcessModulesEx(h, arr, ctypes.sizeof(arr), ctypes.byref(need), 1)
n = need.value // ctypes.sizeof(wt.HMODULE)
psapi.GetModuleFileNameExW.restype = wt.DWORD
psapi.GetModuleFileNameExW.argtypes = [wt.HANDLE, wt.HMODULE, wt.LPWSTR, wt.DWORD]
rows = []
for i in range(n):
    base = int(arr[i])
    b = ctypes.create_unicode_buffer(1024)
    psapi.GetModuleFileNameExW(h, wt.HMODULE(base), b, 1024)
    rows.append((base, b.value))

print("=== 游戏目录 / 可疑模块 ===")
for base, path in sorted(rows):
    low = path.lower()
    if any(k in low for k in ["saints row", "sr2", "dfengine", "juiced", "mod", "cn", "han", "patch"]):
        print("  0x%08X  %s" % (base, path))

print()
print("=== 全部非系统模块 ===")
for base, path in sorted(rows):
    low = path.lower()
    if not any(k in low for k in ["system32", "winsxs", "syswow64", "windows\\"]):
        print("  0x%08X  %s" % (base, path))

print()
print("=== 0x7F4430 当前字节 ===")
b = rd(0x7F4430, 8)
print("  ", b.hex(" "))
if b and b[0] == 0xE9:
    tgt = 0x7F4430 + 5 + struct.unpack("<i", b[1:5])[0]
    print("  -> JMP 0x%08X" % tgt)
    t = (tgt - (tgt & ~0xFFFF))  # placeholder
    print("  桩区域: 0x%08X ~ 0x%08X" % (tgt, tgt + 0x100))

# shellcode 特征搜索：找哪个模块包含桩的字节序列
print()
print("=== 搜索桩字节序列属于哪个模块 ===")
sig = rd(0x5B8701A5, 0x80)
if sig:
    mods = []
    for base, path in sorted(rows):
        mods.append((base, path))
    # 直接在各模块磁盘文件里搜 sig 前 24 字节
    needle = sig[:24]
    print("  needle =", needle.hex(" "))
    for base, path in sorted(rows):
        try:
            if not os.path.exists(path):
                continue
            data = open(path, "rb").read()
            idx = data.find(needle)
            if idx >= 0:
                print("  ★ 命中 %s @ 文件偏移 0x%X (base=0x%08X -> VA 0x%08X)" % (
                    os.path.basename(path), idx, base, base + idx))
        except Exception as e:
            pass
print("  搜索完毕")
