import ctypes, ctypes.wintypes as wt

pid = None
# 先找 PID
import subprocess
out = subprocess.run(['tasklist'], capture_output=True, text=True, shell=True).stdout
for line in out.splitlines():
    if line.lower().startswith('sr2_pc.exe'):
        pid = int(line.split()[1]); break
print('SR2_pc PID =', pid)
assert pid

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
k32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi
h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
if not h:
    raise SystemExit('OpenProcess 失败 errno=%d' % k32.GetLastError())
print('句柄 OK: %#x' % h)

LIST_MODULES_32BIT = 0x01
N = 2048
arr = (ctypes.c_ulong * N)()
needed = wt.DWORD()
ok = psapi.EnumProcessModulesEx(h, ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(needed), LIST_MODULES_32BIT)
print('EnumProcessModulesEx =', ok, ' needed =', needed.value)
if not ok:
    raise SystemExit('枚举失败 errno=%d' % k32.GetLastError())

cnt = needed.value // ctypes.sizeof(ctypes.c_ulong)
print('模块数:', cnt)

GetModuleFileNameExW = psapi.GetModuleFileNameExW
GetModuleFileNameExW.restype = wt.DWORD
GetModuleFileNameExW.argtypes = [wt.HANDLE, ctypes.c_ulong, ctypes.c_wchar_p, wt.DWORD]

mods = []
for i in range(cnt):
    buf = ctypes.create_unicode_buffer(1024)
    n = GetModuleFileNameExW(h, arr[i], buf, 1024)
    if n:
        mods.append(buf.value)

import re
print()
print('=== 关注的模块 ===')
pat = re.compile(r'(?i)(cheight|\.asi$|dinput|dfengine|binkw|d3d9|reshade|dsound|sdl3|xlive|juiced|winmm|version\.dll|dlss5|dgvoodoo)')
for m in mods:
    if pat.search(m):
        print('  ', m)
print()
print('=== 全部模块路径（去重后前 40）===')
for m in sorted(set(mods))[:40]:
    print('  ', m)
