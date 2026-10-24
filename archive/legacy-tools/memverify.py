# -*- coding: utf-8 -*-
"""读 SR2 进程内存，比对运行时实际加载的 charlist / vf3 / static_CH 与磁盘文件是否一致。"""
import ctypes, ctypes.wintypes as wt, struct, sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
OpenProcess = k32.OpenProcess; OpenProcess.restype = wt.HANDLE
ReadProcessMemory = k32.ReadProcessMemory
ReadProcessMemory.argtypes = [wt.HANDLE, wt.LPCVOID, wt.LPVOID, ctypes.c_size_t,
                             ctypes.POINTER(ctypes.c_size_t)]
VirtualQueryEx = k32.VirtualQueryEx
VirtualQueryEx.argtypes = [wt.HANDLE, wt.LPCVOID, wt.LPVOID, ctypes.c_size_t]

PID = int(sys.argv[1])
h = OpenProcess(PID, 0x0010 | 0x0400, None)      # VM_READ | QUERY_INFO
if not h:
    print("OpenProcess 失败 err=%d" % ctypes.get_last_error()); sys.exit(1)

def read(addr, n):
    buf = ctypes.create_string_buffer(n); got = ctypes.c_size_t()
    if not ReadProcessMemory(h, ctypes.c_void_p(addr), buf, n, ctypes.byref(got)):
        return None
    return buf.raw[:got.value]

def regions():
    out, addr = [], 0x10000
    vq = ctypes.create_string_buffer(48)
    while addr < 0x7FFF0000:
        if not VirtualQueryEx(h, ctypes.c_void_p(addr), vq, 48):
            break
        q = ctypes.cast(vq, ctypes.POINTER(wt.MEMORY_BASIC_INFORMATION)).contents
        base, size = int(q.BaseAddress), int(q.RegionSize)
        if q.State == 0x1000 and (q.Protect & 0x04) and size > 0:
            out.append((base, size))
        addr = base + size
        if addr <= base:
            break
    return out

REGIONS = regions()
print("可读区域 %d 个，合计 %.1f MB" % (len(REGIONS), sum(s for _, s in REGIONS) / 1048576.0))

def find(pat, cap=20):
    hits, st = [], 0
    for base, size in REGIONS:
        d = read(base, size)
        if not d:
            continue
        st = 0
        while True:
            i = d.find(pat, st)
            if i < 0:
                break
            hits.append(base + i)
            st = i + 1
            if len(hits) >= cap:
                return hits
    return hits

def seq(*slots):
    return b"".join(struct.pack(">H", s) for s in slots)

# --- 磁盘基准 ---
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
static = bytes(v.read(v.find("static_CH", "le_strings")))
vf3 = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
U_OFF, V_OFF = 0xAF6C, 0xDB18
NU = 2795
U = list(struct.unpack_from("<%di" % NU, vf3, U_OFF))
V = list(struct.unpack_from("<%di" % NU, vf3, V_OFF))
def dec(slots): return "".join(chr(cps[s - 0x20]) for s in slots)

tests = [
    ("U数组头(1,32,63..)", b"".join(struct.pack("<i", 1 + 31 * t) for t in range(8))),
    ("charlist头(32\\n33..)", b"32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n"),
    ("斯蒂尔沃特slot", seq(1379, 2254, 952, 1601, 1773)),
    ("辩护律师slot",    seq(2506, 1222, 1089, 1013)),
    ("辩护延师slot",    seq(2506, 1222, 1057, 1013)),
]
for name, pat in tests:
    hits = find(pat)
    print("\n%-20s 内存命中 %d" % (name, len(hits)))
    for a in hits[:4]:
        print("    @0x%08X" % a)

# 关键：若内存里存在 charlist 文本，解析它，看 slot 1089 到底是什么
raw_pat = b"32\n33\n34\n35\n36\n37\n38\n39\n40\n41\n42\n43\n44\n45\n"
for a in find(raw_pat, 8):
    d = read(a, 60000)
    if not d:
        continue
    end = d.find(b"//ENDOFFILE")
    if end < 0:
        continue
    mem = [int(x) for x in d[:end].decode("utf-8", "ignore").split("\n") if x.strip().isdigit()]
    print("\n★ 内存中发现完整字表：%d 项（磁盘 %d 项）" % (len(mem), len(cps)))
    if mem == cps:
        print("  ✓ 与磁盘 charlist_CH 完全一致")
    else:
        diff = [i for i in range(min(len(mem), len(cps))) if mem[i] != cps[i]]
        print("  ✗ 与磁盘不同，前 %d 处差异: %s" % (len(diff), diff[:12]))
        for i in diff[:6]:
            print("      idx %-5d 内存 U+%04X(%s)  磁盘 U+%04X(%s)"
                  % (i, mem[i], chr(mem[i]), cps[i], chr(cps[i])))
    break