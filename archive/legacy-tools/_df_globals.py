# -*- coding: utf-8 -*-
"""读取运行时 DFEngine 的 g_CustomStrings / g_CustomPadStrings / increase_localization_buffer
等关键全局对象。base = 0x5C640000 (DFEngine runtime base)。
RVA -> VA: VA = 0x5C640000 + RVA
"""
import sys, struct
sys.stdout.reconfigure(encoding="utf-8")
import ce_mini as C

pid = C.find_pid(); h = C.open_process(pid)


def rd(a, n):
    return C.read_mem(h, a, n)


def u32(a):
    b = rd(a, 4); return struct.unpack("<I", b)[0] if b and len(b) == 4 else None


def u64(a):
    b = rd(a, 8); return struct.unpack("<Q", b)[0] if b and len(b) == 8 else None


RT = 0x5C640000


def va(rva):
    return RT + rva


print("pid =", pid)
print("DFEngine RT base = 0x%08X" % RT)

# 先确认 DFEngine base 是否正确：读 0x5C640000 的 MZ
mz = rd(RT, 2)
print("0x5C640000 头 =", mz.hex(" "), "(应 4d 5a)")

g_CustomStrings = va(0x1B54CFC)
print("\ng_CustomStrings VA = 0x%08X" % g_CustomStrings)
# ankerl unordered_dense table 布局:
#  struct table {
#    value_container m_values;   // vector<pair<Key,T>>: {T* beg; T* end; T* cap} = 12 bytes
#    bucket_container m_buckets; // vector<bucket>: {b* beg; b* end; b* cap} = 12 bytes
#    size_t m_num_buckets; uint8_t m_max_load_factor; ...
#  }
raw = rd(g_CustomStrings, 64)
print("raw 64B:", raw.hex(" "))
vals = struct.unpack("<9I", raw[:36])
print("m_values  beg=0x%08X end=0x%08X cap=0x%08X" % (vals[0], vals[1], vals[2]))
print("m_buckets beg=0x%08X end=0x%08X cap=0x%08X" % (vals[3], vals[4], vals[5]))
print("next:", vals[6:9])
