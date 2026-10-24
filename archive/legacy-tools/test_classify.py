# -*- coding: utf-8 -*-
"""验证字节序甄别：必须能区分「真 LE 字符串」与「BE 数据的错位命中」

★ 背景：UTF-16BE 的 `4E FB` 从下一字节读就是 LE 的开头，两者相距半个码元，
  搜索时会互相命中。若甄别不了，同一份数据会被误判成两份。
"""
import sys, subprocess, time, struct
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C
from ctypes import create_string_buffer, byref, c_size_t

C.enable_debug_privilege()
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(200)"])
time.sleep(1.5)
h = C.open_process(child.pid)

TEXT = "任璨偶巧位"                # 用真实的乱码串，贴近实战
pat_le = C.le(TEXT)
first_cp = struct.unpack_from("<H", pat_le, 0)[0]
print("串=%r  首字码点=U+%04X  LE模式=%s" % (TEXT, first_cp, pat_le.hex(" ").upper()))

def write(blob, off=0):
    remote = C.VirtualAllocEx(h, None, 4096, 0x3000, 0x04)
    if off:
        remote = remote + off
    buf = create_string_buffer(blob, len(blob))
    w = c_size_t(0)
    ok = C.WriteProcessMemory(h, C.ctypes.c_void_p(remote), buf, len(blob), byref(w))
    assert ok, "写入失败"
    C.k32.CloseHandle(h)
    return remote

try:
    # ---- 情形1：写入 BE 编码 -> 搜 LE 应当在 +1 处错位命中，甄别要说"BE错位" ----
    h = C.open_process(child.pid)
    base_be = write(C.be(TEXT))
    hits = C.scan_process(h, [("LE", pat_le, "")], C.addr_limit(h))[0]["LE"]
    print("\n[情形1] 内存里是 UTF-16BE，搜 LE：命中 %d 处" % len(hits))
    assert hits, "应错位命中"
    for a in hits:
        print("   0x%X -> %s" % (a, C.classify_enc_hit(h, a, pat_le)))
        ok = ("错位" in C.classify_enc_hit(h, a, pat_le))
        assert ok, "甄别失败：应识别为 BE 错位命中"
    print("   ★ 正确识别为 BE 错位命中")

    # ---- 情形2：写入真 LE（后随 00 00 终止符）-> 甄别要说"真正的 LE" ----
    h = C.open_process(child.pid)
    base_le = write(C.le(TEXT) + b"\x00\x00")
    hits2 = C.scan_process(h, [("LE", pat_le, "")], C.addr_limit(h))[0]["LE"]
    # 情形1 的内存还在，会一起搜到；只甄别属于情形2 的那个地址
    print("\n[情形2] 内存里是真 UTF-16LE(+终止符)，搜 LE：命中 %d 处" % len(hits2))
    mine = [a for a in hits2 if a == base_le or a == base_le + 0]
    for a in [base_le]:
        k = C.classify_enc_hit(h, a, pat_le)
        print("   0x%X (写入地址 0x%X) -> %s" % (a, base_le, k))
        assert "真正的" in k, "甄别失败，开发者元数据=%r" % k
    print("   ★ 正确识别为真 LE 字符串")
    print("\n★★ 字节序甄别通过：同一份数据不会再被误判成两份")
finally:
    pass
