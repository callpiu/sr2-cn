# -*- coding: utf-8 -*-
"""定位「错误的 slot->Unicode 转换表」

已知 9 组映射（charlist_CH 索引 -> 屏幕上实际显示的汉字 Unicode）：
    们332->位  你371->任  保391->伪  兄422->巧  弟1035->偶
    护1190->该 的1836->璨 要2296->衡 需2667->雄
若某张表 T 满足 T[idx] = 那个 Unicode，则 T 就是罪魁祸首。
用「跨 distance 的双锚点 + 通配符」先粗筛，再逐条验证其余映射，避免误报。
"""
import sys, struct, re, time
sys.path.insert(0, "F:/sr2-cn")
import ce_mini as C

PAIRS = [(332, 0x4F4D), (371, 0x4EFB), (391, 0x4F2A), (422, 0x5DE7),
         (1055, 0x5076), (1190, 0x8BE5), (1836, 0x743F),
         (2296, 0x8861), (2667, 0x96C4)]

C.enable_debug_privilege()
pid = C.find_pid()
h = C.open_process(pid)
lim = C.addr_limit(h)
print("pid=%d  上限 0x%X" % (pid, lim))

def le_u(cp): return struct.pack("<H", cp)

found = []
for stride in (2, 4):
    anchor0, anchor1 = PAIRS[0], PAIRS[1]
    gap = (anchor1[0] - anchor0[0]) * stride - 2
    pat = re.compile(re.escape(le_u(anchor0[1])) + b".{%d}" % gap +
                     re.escape(le_u(anchor1[1])), re.S)
    maxidx = max(p[0] for p in PAIRS)
    span = maxidx * stride + 4
    print("\n--- stride=%d  锚点间距=%d字节  模式=%s... " % (
        stride, gap, pat.pattern[:12].hex(" ").upper()))

    ncand = 0
    for base, size, prot in C.enum_regions(h, lim):
        if size < span: continue
        pos = 0
        raw = C.read_mem(h, base, min(size, 64 * 1024 * 1024))
        if raw is None: continue
        for m in pat.finditer(raw):
            ncand += 1
            cand = base + m.start() - anchor0[0] * stride
            if cand < base: continue
            tbl = C.read_mem(h, cand, span)
            if tbl is None: continue
            # 逐条验证全部 9 组
            ok = 0
            for idx, cp in PAIRS:
                off = idx * stride
                if off + 2 > len(tbl): break
                if struct.unpack_from("<H", tbl, off)[0] == cp:
                    ok += 1
            if ok >= 5:
                print("  ★ 候选表基址 0x%X  验证通过 %d/%d" % (cand, ok, len(PAIRS)))
                found.append((cand, stride, ok))
        pos += size
    print("  候选 %d 个" % ncand)

print("\n" + "=" * 70)
if found:
    cand, stride, ok = max(found, key=lambda x: x[2])
    print("★ 找到转换表: 0x%X  stride=%d  验证 %d/%d" % (cand, stride, ok, len(PAIRS)))
    tbl = C.read_mem(h, cand, 40)
    print("  表头 40B: %s" % (tbl or b"").hex(" ").upper())
    for idx, cp in PAIRS:
        u = struct.unpack_from("<H", C.read_mem(h, cand + idx * stride, 2), 0)[0]
        print("    idx %4d -> U+%04X %s  %s" % (
            idx, u, chr(u), "OK" if u == cp else "<- 不符"))
else:
    print("未找到。可能转换表当前不在内存（需要在触发字幕时扫），")
    print("或者这种索引假设不成立（表可能不是简单的 u16 数组）。")
C.k32.CloseHandle(h)
