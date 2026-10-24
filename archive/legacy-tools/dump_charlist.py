# -*- coding: utf-8 -*-
"""运行时读取引擎字表（无 ASLR，ImageBase=0x400000，静态VA即绝对地址）"""
import ctypes, struct, sys, json
from ctypes import wintypes

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wintypes.HANDLE
k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.ReadProcessMemory.restype = wintypes.BOOL
k32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.CloseHandle.restype = wintypes.BOOL
k32.CloseHandle.argtypes = [wintypes.HANDLE]

PID = 4868
h = k32.OpenProcess(0x001F0FFF, False, PID)
print("PID=%d handle=%s err=%d" % (PID, h, ctypes.get_last_error()))

def rd(addr, n):
    b = (ctypes.c_ubyte * n)()
    got = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(h, ctypes.c_void_p(addr), b, n, ctypes.byref(got))
    return bytes(b) if ok and got.value == n else None

PTR_VA, CNT_VA = 0x02528B2C, 0x02528B30
pb, cb = rd(PTR_VA, 4), rd(CNT_VA, 4)
print("CHARLIST_PTR @0x%08X = %s" % (PTR_VA, pb.hex() if pb else "FAIL"))
print("NUM_CCHARS   @0x%08X = %s" % (CNT_VA, cb.hex() if cb else "FAIL"))
if not pb or not cb:
    sys.exit("读取失败")
clptr, num = struct.unpack("<II", pb + cb)
print("=> 字表指针 0x%08X   条目数 %d" % (clptr, num))
if not (0 < num < 100000):
    sys.exit("条目数异常，地址假设可能不对")

raw = rd(clptr, num * 4)
if raw is None:
    sys.exit("字表读取失败")
vals = list(struct.unpack("<%dI" % num, raw))
lo = [v & 0xFFFF for v in vals]
hi = [v >> 16 for v in vals]
print("\n低16位(码点) 前24:", " ".join("%04X" % x for x in lo[:24]))
print("低16位 末12:", " ".join("%04X" % x for x in lo[-12:]))
print("高16位 前24:", " ".join("%04X" % x for x in hi[:24]))
print("高16位 去重 %d 个, 值域 0x%X-0x%X" % (len(set(hi)), min(hi), max(hi)))
print("低16位严格升序:", all(lo[i] < lo[i+1] for i in range(num-1)))
print("低16位唯一码点:", len(set(lo)))

json.dump({"ptr": clptr, "num": num, "lo": lo, "hi": hi},
          open(r"F:\sr2-cn\_runtime_charlist.json", "w"))
print("\n已存 _runtime_charlist.json")

exp = json.load(open(r"F:\sr2-cn\_day_2026-10-07\04_规则与数据\_expected_charlist.json"))
print("\n=== vs _expected_charlist.json (v37, %d 项) ===" % len(exp))
if num == len(exp):
    d = [i for i in range(num) if lo[i] != exp[i]]
    print("  完全一致" if not d else "  差异 %d 项, 前20: %s" % (len(d), d[:20]))
    for i in d[:10]:
        print("    [%d] runtime 0x%04X vs v37 0x%04X" % (i, lo[i], exp[i]))
else:
    print("  条数不同: runtime %d vs v37 %d" % (num, len(exp)))

def load_cl(p):
    xs = []
    for l in open(p, encoding='utf-8'):
        l = l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
cl = load_cl(r"F:\sr2-cn\_juice_fix\charlist_CH.txt")
print("\n=== vs charlist_CH.txt (%d 项, 汉化重建/已排序) ===" % len(cl))
print("  交集 %d, runtime独有 %d, charlist_CH独有 %d"
      % (len(set(lo) & set(cl)), len(set(lo) - set(cl)), len(set(cl) - set(lo))))

print("\n=== 9 个乱码锚点在 runtime 字表中的位置 ===")
OBS = [("们",0x4EEC,0x4F4D),("你",0x4F60,0x4EFB),("保",0x4FDD,0x4F2A),
       ("兄",0x5144,0x5DE7),("弟",0x5F1F,0x5076),("护",0x62A4,0x8BE5),
       ("的",0x7684,0x74A8),("要",0x8981,0x8861),("需",0x9700,0x96C4)]
pos = {cp: i for i, cp in enumerate(lo)}
for ch, cp, out in OBS:
    pi, po = pos.get(cp), pos.get(out)
    print("  %s U+%04X @%s   ->  U+%04X @%s" % (ch, cp, pi, out, po))
