# -*- coding: utf-8 -*-
"""内存扫描 v2（带正对照）：
 A. 正确字表 charlist_CH 作为 u16 数组（正对照，必须命中否则扫描链无效）
 B. 错误转换表 T：arr[332]=0x4F4D, arr[371]=0x4EFB, arr[391]=0x4F2A, arr[422]=0x5DE7,
    arr[1035]=0x5076, arr[1190]=0x8BE5, arr[1836]=0x74A8, arr[2296]=0x8861, arr[2667]=0x96C4
 C. common 字体码点表：arr[332]=0x4F5C(作), arr[359]=0x5012(倒), arr[371]=0x5065(健),
    arr[390]=0x50CF(像), arr[1003]=0x5FD7(志), arr[1158]=0x633D(捍),
    arr[1804]=0x76EF(盯), arr[2264]=0x91CC(里), arr[2635]=0x9664(除)
 D. HUD 宽字缓冲「任璨偶巧位」LE，定位后 dump 邻居
"""
import sys, os, struct, time
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import ce_mini as C

C.enable_debug_privilege()
pid = C.find_pid()
h = C.open_process(pid)
lim = C.addr_limit(h)
print("pid=%d  位数上限=0x%X" % (pid, lim))

CORRECT = {332: 0x4EEC, 371: 0x4F60, 391: 0x4FDD, 422: 0x5144, 1035: 0x5F1F,
           1190: 0x62A4, 1836: 0x7684, 2296: 0x8981, 2667: 0x9700}
WRONG = {332: 0x4F4D, 371: 0x4EFB, 391: 0x4F2A, 422: 0x5DE7, 1035: 0x5076,
         1190: 0x8BE5, 1836: 0x74A8, 2296: 0x8861, 2667: 0x96C4}
COMMON = {332: 0x4F5C, 359: 0x5012, 371: 0x5065, 390: 0x50CF, 1003: 0x5FD7,
          1158: 0x633D, 1804: 0x76EF, 2264: 0x91CC, 2635: 0x9664}

WIDE_LE = "任璨偶巧位".encode("utf-16-le")
WIDE_LE2 = "任璨偶".encode("utf-16-le")

def scan_array(pairs, stride, endian, label, results, maxhits=60):
    fmt = ("<" if endian == "LE" else ">") + ("H" if stride == 2 else "I")
    items = sorted(pairs.items())
    base_b = struct.pack(fmt, items[0][1])
    rest = [(i * stride, struct.pack(fmt, cp)) for i, cp in items[1:]]
    chunk = 0x400000
    ov = 1 << 16
    for rbase, size, prot in C.enum_regions(h, lim):
        pos = 0
        prev = b""
        while pos < size:
            want = min(chunk, size - pos)
            raw = C.read_mem(h, rbase + pos, want)
            if raw is None:
                pos += want
                prev = b""
                continue
            data = prev + raw
            st = 0
            while True:
                i = data.find(base_b, st)
                if i < 0:
                    break
                st = i + 1
                if all(data[i + off:i + off + len(b)] == b for off, b in rest):
                    addr = rbase + pos - len(prev) + i
                    results.append((label, addr, "prot=0x%X" % prot))
                    if len(results) >= maxhits:
                        return
            prev = data[-ov:]
            pos += want

t0 = time.time()
print("开始扫描（约 2GB，预计 1-3 分钟）...")

# A. 正对照：ASCII 前缀 20 00 21 00 ... (u16 LE 字表开头)
for en, pre in (("LE", bytes(range(0x20, 0x2A)).hex()), ):
    pass
res_ascii_le, res_ascii_be = [], []
for label, pat, out in (("ASCII_LE", b"\x20\x00\x21\x00\x22\x00\x23\x00\x24\x00\x25\x00", res_ascii_le),
                        ("ASCII_BE", b"\x00\x20\x00\x21\x00\x22\x00\x23\x00\x24\x00\x25", res_ascii_be)):
    chunk = 0x400000
    ov = 64
    for rbase, size, prot in C.enum_regions(h, lim):
        pos = 0
        prev = b""
        while pos < size:
            want = min(chunk, size - pos)
            raw = C.read_mem(h, rbase + pos, want)
            if raw is None:
                pos += want
                prev = b""
                continue
            data = prev + raw
            st = 0
            while True:
                i = data.find(pat, st)
                if i < 0:
                    break
                st = i + 1
                out.append((label, rbase + pos - len(prev) + i, "prot=0x%X" % prot))
                if len(out) >= 40:
                    break
            prev = data[-ov:]
            pos += want
        if len(out) >= 40:
            break
    print("[%s] %d 处 (%.0fs)" % (label, len(out), time.time() - t0))
    for a in out[:6]:
        print("     0x%08X %s" % (a[1], a[2]))

# B/C. 锚点数组
res_arr = []
for name, pairs in (("CORRECT", CORRECT), ("WRONG", WRONG), ("COMMON", COMMON)):
    for stride in (2, 4):
        for en in ("LE", "BE"):
            scan_array(pairs, stride, en, "%s_%s_%d" % (name, en, stride), res_arr)
            print("  ...%s stride%d %s 完成, 累计命中 %d (%.0fs)" % (name, stride, en, len(res_arr), time.time() - t0))
print("\n=== 锚点数组命中 %d 处 ===" % len(res_arr))
seen = set()
for lb, a, p in res_arr:
    k = (lb, a)
    if k in seen:
        continue
    seen.add(k)
    print("   %-18s 0x%08X %s" % (lb, a, p))

# D. HUD 宽字缓冲
res_wide = []
for label, pat in (("WIDE_任璨偶巧位", WIDE_LE), ("WIDE_任璨偶", WIDE_LE2)):
    chunk = 0x400000
    ov = 64
    for rbase, size, prot in C.enum_regions(h, lim):
        pos = 0
        prev = b""
        while pos < size:
            want = min(chunk, size - pos)
            raw = C.read_mem(h, rbase + pos, want)
            if raw is None:
                pos += want
                prev = b""
                continue
            data = prev + raw
            st = 0
            while True:
                i = data.find(pat, st)
                if i < 0:
                    break
                st = i + 1
                res_wide.append((label, rbase + pos - len(prev) + i, "prot=0x%X" % prot))
                if len(res_wide) >= 30:
                    break
            prev = data[-ov:]
            pos += want
        if len(res_wide) >= 30:
            break
print("\n=== HUD 宽字缓冲命中 %d 处 ===" % len(res_wide))
for lb, a, p in res_wide[:10]:
    print("   %s 0x%08X %s" % (lb, a, p))
    raw = C.read_mem(h, a - 64, 256)
    if raw:
        print("     上下文: %s" % raw[:96].hex(" "))
        try:
            print("     LE解码: %r" % raw[64:64 + 60].decode("utf-16-le", "replace"))
        except Exception:
            pass

print("\n总耗时 %.0f 秒" % (time.time() - t0))
C.k32.CloseHandle(h)
