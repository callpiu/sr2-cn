# -*- coding: utf-8 -*-
"""双向验证字节序甄别（用真实的 [format][color:green] 标签）
  A: 内存 BE 存储 -> 搜 LE 应在 base+1 错位命中，甄别须说「错位」
  B: 内存 LE 存储 -> 搜 LE 应在 base   正常命中，甄别须说「真字符串」
"""
import sys, subprocess, time
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C
from ctypes import create_string_buffer, byref, c_size_t

C.enable_debug_privilege()
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"])
time.sleep(1.5)
TAG = "[format][color:green]"
pat_le, pat_be = C.le(TAG), C.be(TAG)

def put(blob):
    h = C.open_process(child.pid)
    remote = C.VirtualAllocEx(h, None, 4096, 0x3000, 0x04)
    buf = create_string_buffer(blob, len(blob))
    w = c_size_t(0)
    ok = C.WriteProcessMemory(h, C.ctypes.c_void_p(remote), buf, len(blob), byref(w))
    C.k32.CloseHandle(h)
    assert ok and w.value == len(blob), "写入失败"
    return remote

base_be = put(pat_be)                 # A: BE 存储
base_le = put(pat_le + b"\x00\x00")   # B: LE 存储 + 终止符
print("BE 数据写在 0x%X\nLE 数据写在 0x%X" % (base_be, base_le))

h = C.open_process(child.pid)
res, scanned, total, dt, nreg = C.scan_process(
    h, [("TAG_LE", pat_le, ""), ("TAG_BE", pat_be, "")], C.addr_limit(h))
print("扫描 %.1f 秒 / %.0f MB / %d 区" % (dt, scanned/1e6, nreg))

for name, pat in [("TAG_LE", pat_le), ("TAG_BE", pat_be)]:
    print("\n【%s】命中 %d 处" % (name, len(res[name])))
    for a in res[name]:
        k = C.classify_enc_hit(h, a, pat)
        print("   0x%X  %s" % (a, k))

# --- 断言 ---
def assert_is(addr, pat, kw, desc):
    k = C.classify_enc_hit(h, addr, pat)
    assert kw in k, "%s 失败: %r" % (desc, k)
    print("★ %s -> %s" % (desc, k.split('←')[1].strip()[:46]))

print()
assert (base_be + 1) in res["TAG_LE"], "A: BE 数据应被 LE 搜索错位命中"
assert_is(base_be + 1, pat_le, "错位", "A1 BE存储被LE搜到(+1)")
assert base_be in res["TAG_BE"], "A: BE 数据应被 BE 搜索命中"
assert_is(base_be, pat_be, "真字符串", "A2 BE存储被BE搜到")
assert base_le in res["TAG_LE"], "B: LE 数据应被 LE 搜索命中"
assert_is(base_le, pat_le, "真字符串", "B1 LE存储被LE搜到")
assert (base_le - 1) in res["TAG_BE"], "B: LE 数据应被 BE 搜索错位命中"
assert_is(base_le - 1, pat_be, "错位", "B2 LE存储被BE搜到(-1)")

print("\n★★★ 字节序甄别双向验证通过")
print("   同一份 ASCII 数据会被两种字节序各命中一次，甄别能正确标注哪份是真数据")
C.k32.CloseHandle(h); child.kill()
