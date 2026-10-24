# -*- coding: utf-8 -*-
"""补验 B2：LE 数据被 BE 搜索错位命中(base-1)。
前置条件：错位成立需要数据【前一字节恰好是 0x00 且可读】。
所以把 LE 数据写在 pad 字节之后（而不是页首），人为造出这个条件。
另修：子进程必须 stdout=DEVNULL，否则继承管道导致上层 tail 一直等待。
"""
import sys, subprocess, time
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C
from ctypes import create_string_buffer, byref, c_size_t

C.enable_debug_privilege()
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
TAG = "[format][color:green]"
pat_le, pat_be = C.le(TAG), C.be(TAG)

h = C.open_process(child.pid)
remote = C.VirtualAllocEx(h, None, 4096, 0x3000, 0x04)
blob = b"\x00" + pat_le + b"\x00\x00"        # 前面垫一个 0x00：制造错位条件
buf = create_string_buffer(blob, len(blob))
w = c_size_t(0)
assert C.WriteProcessMemory(h, C.ctypes.c_void_p(remote), buf, len(blob), byref(w))
base_le = remote + 1                          # LE 数据真实起点
print("pad 在 0x%X (值=00)，LE 数据在 0x%X" % (remote, base_le))

res, scanned, total, dt, nreg = C.scan_process(
    h, [("TAG_LE", pat_le, ""), ("TAG_BE", pat_be, "")], C.addr_limit(h))
print("扫描 %.1f 秒 / %.0f MB / %d 区" % (dt, scanned/1e6, nreg))
for name, pat in [("TAG_LE", pat_le), ("TAG_BE", pat_be)]:
    print("\n【%s】命中 %d 处" % (name, len(res[name])))
    for a in res[name]:
        print("   0x%X  %s" % (a, C.classify_enc_hit(h, a, pat)))

assert base_le in res["TAG_LE"], "B1 失败: LE 数据应被 LE 搜索命中"
print("\n★ B1 LE存储被LE搜到 ->", C.classify_enc_hit(h, base_le, pat_le).split('←')[1].strip()[:40])
assert (base_le - 1) in res["TAG_BE"], "B2 失败: LE 数据应被 BE 搜索在 base-1 错位命中"
k = C.classify_enc_hit(h, base_le - 1, pat_be)
assert "错位" in k, "B2 甄别失败: %r" % k
print("★ B2 LE存储被BE搜到(-1) ->", k.split('←')[1].strip()[:40])
print("\n★★★ 双向错位甄别全部通过（A/B 两种字节序都能正确标注）")
C.k32.CloseHandle(h); child.kill()
