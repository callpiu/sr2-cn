# -*- coding: utf-8 -*-
"""跨进程正/负样本自检（比扫自己进程严谨）

★ 为什么要跨进程：扫描自己进程时，你构造过的任何字符串都以 ASCII 形式存在
  于自己的堆内存里，'负样本'必然命中 → 只能验链路，验不了零误报。
  用一个全新子进程做目标，才能真正区分"真命中"和"误报"。
"""
import sys, os, subprocess, time
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

C.enable_debug_privilege()

# 全新 python 子进程，不可能持有我们这边构造的字符串
child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
print("子进程 pid=%d" % child.pid)
time.sleep(1.5)

h = C.open_process(child.pid)
lim = C.addr_limit(h)
print("子进程位数: %s, 上限 0x%X" % ("32 位" if lim == 0x7FFFFFFF else "64 位", lim))

marker_text = "SR2XPROCMARKER01"
marker_be = C.be(marker_text)              # UTF-16BE —— 真正要写进去的
never1 = "ZZQQNEVERWRITTEN99"              # 从未写入：负样本
never_be = C.be(never1)

MEM_COMMIT_RESERVE = 0x3000
PAGE_READWRITE = 0x04
remote = C.VirtualAllocEx(h, None, 4096, MEM_COMMIT_RESERVE, PAGE_READWRITE)
print("远端分配: 0x%X" % (remote or 0))
assert remote, "VirtualAllocEx 失败"

from ctypes import create_string_buffer, byref, c_size_t
mbuf = create_string_buffer(marker_be, len(marker_be))
written = c_size_t(0)
ok = C.WriteProcessMemory(h, C.ctypes.c_void_p(remote), mbuf, len(marker_be), byref(written))
print("写入 %d 字节: %s" % (written.value, "成功" if ok else "失败"))
assert ok and written.value == len(marker_be)

pats = [("正样本_BE", marker_be, "刚写入，必命中"),
        ("负样本_BE", never_be, "从未写入，必须 0 命中"),
        ("负样本_LE", C.le(marker_text), "写了BE没写LE，必须 0 命中")]
res, scanned, total, dt, nreg = C.scan_process(h, pats, lim)
print("扫描 %.1f 秒 / %.0f MB / %d 区" % (dt, scanned / 1e6, nreg))
for name, pat, note in pats:
    print("   %-10s 命中 %d 处   %s" % (name, len(res[name]), note))

assert len(res["正样本_BE"]) >= 1, "链路坏了：写了却搜不到"
assert not res["负样本_BE"], "有误报：从未写入的串被'搜到'了"
assert not res["负样本_LE"], "有误报：字节序不同的串被'搜到'了"
print("\n★★ 跨进程自检通过：链路可用 且 零误报")

C.VirtualFreeEx(h, C.ctypes.c_void_p(remote), 0, 0x8000)
C.k32.CloseHandle(h)
child.kill()
