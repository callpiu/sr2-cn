# -*- coding: utf-8 -*-
"""决定性实验：内存里搜「错误 slot->codepoint 转换表」。

锚点全部来自「磁盘解码 + 内存 UTF-16LE 缓存串直读」，无截图转录误差：
    你 slot0x193 -> U+4EFB(任)   的 slot0x74C -> U+74A8(璨)
    弟 slot0x42B -> U+5076(偶)   兄 slot0x1C6 -> U+5DE7(巧)
    们 slot0x16C -> U+4F4D(位)
同时搜「正确字表」(T[0x193]=U+4F60) 作正对照，验证扫描器本身有效。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import ce_mini as CE

CE.enable_debug_privilege()
pid = CE.find_pid()
h = CE.open_process(pid)
print("[mem] pid=%d" % pid)

# (slot, 错误码点, 正确码点, 字)
ANCH = [
    (0x193, 0x4EFB, 0x4F60, "你"),
    (0x74C, 0x74A8, 0x7684, "的"),
    (0x42B, 0x5076, 0x5F1F, "弟"),
    (0x1C6, 0x5DE7, 0x5144, "兄"),
    (0x16C, 0x4F4D, 0x4EEC, "们"),
]
A0_SLOT, A0_BAD, A0_GOOD, A0_CH = ANCH[0]


def scan_u16(val):
    """全内存搜 u16（LE/BE 都试），返回 [(addr, be)]"""
    out = []
    for be in (False, True):
        pat = struct.pack(">H" if be else "<H", val)
        res, scanned, total, dt, nreg = CE.scan_process(
            h, [("v", pat, "")], CE.addr_limit(h))
        for a in res["v"]:
            out.append((a, be))
    return out


def check(addr, be, idx_base, stride):
    """在 addr 处假设为 table[idx_base]，验证其余 4 个锚点"""
    ok = 0
    for slot, bad, good, ch in ANCH[1:]:
        i = slot - idx_base
        if i < 0:
            return -1
        pos = addr + i * stride
        raw = CE.read_mem(h, pos, stride)
        if raw is None or len(raw) < stride:
            return -1
        if stride == 2:
            v = struct.unpack(">H" if be else "<H", raw)[0]
        else:
            w = struct.unpack(">I" if be else "<I", raw)[0]
            v = w & 0xFFFF if not be else (w >> 16) & 0xFFFF
            if be:
                v = (w >> 16) & 0xFFFF
        if v == bad:
            ok += 1
        else:
            return -1
    return ok


print("\n=== 1) 正对照：搜正确字表 T[0x193]=U+4F60(你) ===")
hits_good = scan_u16(A0_GOOD)
print("U+4F60 命中 %d 处" % len(hits_good))
found_good = []
for a, be in hits_good[:6000]:
    for base, bname in ((A0_SLOT, "slot基"), (A0_SLOT - 0x20, "idx基")):
        for stride in (2, 4):
            r = check(a, be, base, stride)
            if r == 4:
                found_good.append((a, be, bname, stride))
                print("  ★ 正确表 @0x%08X %s %s基 stride=%d" % (a, "BE" if be else "LE", bname, stride))
print("正确表候选: %d" % len(found_good))

print("\n=== 2) 主目标：搜错误转换表 T[0x193]=U+4EFB(任) ===")
hits_bad = scan_u16(A0_BAD)
print("U+4EFB 命中 %d 处" % len(hits_bad))
found_bad = []
for a, be in hits_bad[:8000]:
    for base, bname in ((A0_SLOT, "slot基"), (A0_SLOT - 0x20, "idx基")):
        for stride in (2, 4):
            r = check(a, be, base, stride)
            if r == 4:
                found_bad.append((a, be, bname, stride))
                print("  ★★★ 错误转换表 @0x%08X %s %s基 stride=%d  ← 就是它！" % (
                    a, "BE" if be else "LE", bname, stride))
print("错误表候选: %d" % len(found_bad))

# ---- 3) 对找到的错误表，dump 并顺带解出全部映射 ----
for a, be, bname, stride in found_bad[:3]:
    print("\n" + "=" * 70)
    print("★ 错误转换表 @0x%08X (%s, %s, stride=%d) 结构分析" % (a, "BE" if be else "LE", bname, stride))
    print("=" * 70)
    raw = CE.read_mem(h, a - 64, 64 + 3000 * stride)
    if raw is None:
        continue
    print("  前 64 字节: %s" % " ".join("%02X" % c for c in raw[:64]))
    # 读出 slot 0x20..0x300 范围的映射，看有多少非零/连续
    n = 3000
    vals = []
    for i in range(n):
        pos = a + i * stride
        chunk = CE.read_mem(h, pos, stride)
        if chunk is None or len(chunk) < stride:
            break
        if stride == 2:
            vals.append(struct.unpack(">H" if be else "<H", chunk)[0])
        else:
            w = struct.unpack(">I" if be else "<I", chunk)[0]
            vals.append((w >> 16) & 0xFFFF if be else w & 0xFFFF)
    nz = [v for v in vals if v != 0]
    print("  读出 %d 项, 非零 %d 项" % (len(vals), len(nz)))
    print("  前 40 项: %s" % " ".join("%04X" % v for v in vals[:40]))
    # 与正确字表对比：找差异
    print("  slot0x193(你) -> %04X (应为 4F60)" % vals[0x193] if len(vals) > 0x193 else "")
    CE.k32.CloseHandle(h)
    sys.exit(0)

print("\n未找到错误转换表。")
try:
    CE.k32.CloseHandle(h)
except Exception:
    pass
